import subprocess
import socket
import threading
import time
import random
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import ast
from cryptography.fernet import Fernet
import base64
import hashlib
from datetime import datetime
import fcntl
import struct
from tkinter import messagebox

# Clave secreta compartida (debe ser la misma en todos los nodos)
SECRET_KEY = b'tu_clave_secreta_compartida_32_bytes_longitud_'

# Generar una clave Fernet a partir de la clave secreta
def generate_fernet_key(secret_key):
    return base64.urlsafe_b64encode(hashlib.sha256(secret_key).digest())

fernet_key = generate_fernet_key(SECRET_KEY)
cipher_suite = Fernet(fernet_key)

# Función para encriptar un mensaje
def encrypt_message(message):
    if isinstance(message, dict):
        message = str(message)
    return cipher_suite.encrypt(message.encode())

# Función para desencriptar un mensaje
def decrypt_message(encrypted_message):
    return cipher_suite.decrypt(encrypted_message).decode()

# ===============================
# ⚙️ Controlador PID
# ===============================
class PIDController:
    def __init__(self, kp=1.0, ki=0.1, kd=0.01):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0
        self.integral = 0

    def update(self, error):
        self.integral += error
        derivative = error - self.prev_error
        self.prev_error = error
        return self.kp * error + self.ki * self.integral + self.kd * derivative

# ===============================
# 🧠 Nodo descentralizado BATMAN
# ===============================
class NodoBATMAN:
    def __init__(self, gui, puerto=5005):
        self.puerto = puerto
        self.pid = PIDController()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', puerto))
        self.intervalo_envio = 1.0
        self.mensajes_recibidos = 0
        self.lock_mensajes = threading.Lock()
        self.error_actual = 0
        self.ajuste_pid = 0
        self.vector_clock = {socket.gethostname(): 0}
        self.hostname = socket.gethostname()
        self.gui = gui

        self.mac_ip_map = {
            "54:6c:eb:e4:b5:42": "192.168.1.4",
            "58:00:e3:6a:28:79": "192.168.1.2",
        }
        self.tiempo = []
        self.errores = []
        self.t0 = time.time()

    def obtener_vecinos(self, umbral_segundos=10):
        try:
            output = subprocess.check_output(['batctl', 'n'], stderr=subprocess.DEVNULL).decode()
            vecinos_validos = []
            for line in output.splitlines():
                if line.strip() == "" or line.startswith("IF") or line.startswith("["):
                    continue
                partes = line.split()
                if len(partes) < 3:
                    continue
                mac = partes[1]
                last_seen = partes[2]
                if last_seen.endswith('s'):
                    try:
                        segundos = float(last_seen[:-1])
                        if segundos <= umbral_segundos:
                            ip = self.mac_ip_map.get(mac.lower())
                            if ip:
                                vecinos_validos.append(ip)
                    except ValueError:
                        continue
            return vecinos_validos
        except Exception as e:
            print(f"[ERROR al obtener vecinos BATMAN] {e}")
            return []

    def enviar_mensajes(self):
        mensajes_recibidos_previos = 0
        while True:
            vecinos = self.obtener_vecinos()
            if not vecinos:
                print("[ADVERTENCIA] No hay vecinos activos.")
                continue

            ip_destino = random.choice(vecinos)
            self.vector_clock[self.hostname] += 1
            mensaje = {
                "origen": self.hostname,
                "clock": self.vector_clock.copy(),
                "contenido": f"Hola desde {self.hostname}"
            }

            # Encriptar el mensaje antes de enviarlo
            mensaje_encriptado = encrypt_message(mensaje)
            self.sock.sendto(mensaje_encriptado, (ip_destino, self.puerto))
            self.gui.agregar_mensaje_tabla("ENVIADO", ip_destino, mensaje["contenido"], mensaje_encriptado, mensaje["clock"])
            with self.lock_mensajes:
                mensajes_recibidos_actuales = self.mensajes_recibidos

            mensajes_en_este_ciclo = mensajes_recibidos_actuales - mensajes_recibidos_previos
            mensajes_recibidos_previos = mensajes_recibidos_actuales

            self.error_actual = 5 - mensajes_en_este_ciclo
            self.ajuste_pid = self.pid.update(self.error_actual)
            self.intervalo_envio = max(0.5, min(5.0, self.intervalo_envio + self.ajuste_pid))

            t_actual = time.time() - self.t0
            self.tiempo.append(t_actual)
            self.errores.append(self.error_actual)

            self.gui.update_datos(self.error_actual, self.ajuste_pid, self.intervalo_envio, mensajes_recibidos_actuales)
            self.gui.actualizar_grafica(self.tiempo, self.errores)

            time.sleep(self.intervalo_envio)

    def recibir_mensajes(self):
        while True:
            try:
                data, addr = self.sock.recvfrom(4096)

                # Desencriptar el mensaje recibido
                mensaje_encriptado = data
                mensaje_desencriptado = decrypt_message(mensaje_encriptado)
                mensaje = ast.literal_eval(mensaje_desencriptado)

                with self.lock_mensajes:
                    self.mensajes_recibidos += 1

                for nodo, t_remoto in mensaje["clock"].items():
                    if nodo not in self.vector_clock:
                        self.vector_clock[nodo] = 0
                    self.vector_clock[nodo] = max(self.vector_clock[nodo], t_remoto)
                self.vector_clock[self.hostname] += 1

                self.gui.agregar_mensaje_tabla("RECIBIDO", addr[0], mensaje["contenido"], mensaje_encriptado, mensaje["clock"])
            except Exception as e:
                print(f"[ERROR al recibir mensaje] {e}")

    def iniciar(self):
        threading.Thread(target=self.enviar_mensajes, daemon=True).start()
        threading.Thread(target=self.recibir_mensajes, daemon=True).start()

# ===============================
# 🎨 Interfaz gráfica con Tkinter (Modificada con tabla de mensajes)
# ===============================
class InterfazBATMAN:
    def __init__(self, root):
        self.root = root
        self.root.title("Controlador PID & Vector Clocks")
        self.root.geometry("1000x600")

        frame_izquierda = ttk.Frame(root)
        frame_izquierda.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        frame_derecha = ttk.Frame(root)
        frame_derecha.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.var_error = tk.StringVar()
        self.var_ajuste = tk.StringVar()
        self.var_intervalo = tk.StringVar()
        self.var_mensajes = tk.StringVar()

        ttk.Label(frame_izquierda, text="📉 Error actual:").pack()
        ttk.Label(frame_izquierda, textvariable=self.var_error).pack()

        ttk.Label(frame_izquierda, text="🔧 Ajuste PID:").pack()
        ttk.Label(frame_izquierda, textvariable=self.var_ajuste).pack()

        ttk.Label(frame_izquierda, text="⏱️ Intervalo de envío (s):").pack()
        ttk.Label(frame_izquierda, textvariable=self.var_intervalo).pack()

        ttk.Label(frame_izquierda, text="📥 Mensajes recibidos:").pack()
        ttk.Label(frame_izquierda, textvariable=self.var_mensajes).pack()

        self.fig, self.ax = plt.subplots(figsize=(5, 2))
        self.ax.set_title("PID - Error vs Tiempo")
        self.ax.set_xlabel("Tiempo (s)")
        self.ax.set_ylabel("Error")
        self.linea, = self.ax.plot([], [], color='blue')

        self.canvas = FigureCanvasTkAgg(self.fig, master=frame_izquierda)
        self.canvas.get_tk_widget().pack()

        ttk.Button(frame_izquierda, text="Abrir Chat BATMAN", command=lambda: abrir_ventana_chat(self.nodo.vector_clock, self)).pack(pady=10)

        # Tabla de mensajes
        ttk.Label(frame_derecha, text="🗂️ Registro de Mensajes").pack()
        self.tabla_mensajes = ttk.Treeview(frame_derecha, columns=("Tipo", "IP", "Contenido", "Encriptado", "Clock"), show="headings", height=20)
        self.tabla_mensajes.heading("Tipo", text="Tipo")
        self.tabla_mensajes.heading("IP", text="IP")
        self.tabla_mensajes.heading("Contenido", text="Contenido")
        self.tabla_mensajes.heading("Encriptado", text="Encriptado")
        self.tabla_mensajes.heading("Clock", text="Vector Clock")

        self.tabla_mensajes.column("Tipo", width=80)
        self.tabla_mensajes.column("IP", width=150)
        self.tabla_mensajes.column("Contenido", width=400)
        self.tabla_mensajes.column("Encriptado", width=300)
        self.tabla_mensajes.column("Clock", width=200)
        self.tabla_mensajes.pack(fill="both", expand=True)

    def set_nodo(self, nodo):
        self.nodo = nodo

    def update_datos(self, error, ajuste, intervalo, mensajes):
        def actualizar():
            self.var_error.set(f"{error:.2f}")
            self.var_ajuste.set(f"{ajuste:.2f}")
            self.var_intervalo.set(f"{intervalo:.2f}")
            self.var_mensajes.set(str(mensajes))
        self.root.after(0, actualizar)

    def actualizar_grafica(self, tiempo, errores):
        def actualizar():
            self.linea.set_data(tiempo, errores)
            self.ax.relim()
            self.ax.autoscale_view()
            self.canvas.draw()
        self.root.after(0, actualizar)

    def agregar_mensaje_tabla(self, tipo, ip, contenido, mensaje_encriptado, clock:None):
        if clock is None:
            clock = {}
        clock_str = str(clock)
        self.root.after(0, lambda: self.tabla_mensajes.insert("", tk.END, values=(tipo, ip, contenido, mensaje_encriptado, clock_str)))

# ===============================
# Ventana de chat manual
# ===============================
def abrir_ventana_chat(vector_clock, gui):
    PUERTO = 5000
    BUFFER_SIZE = 1024

    def obtener_ip_local():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            ip = socket.inet_ntoa(fcntl.ioctl(
                s.fileno(),
                0x8915,
                struct.pack('256s', b'bat0'[:15])
            )[20:24])
            return ip
        except Exception:
            return None

    def obtener_nombre():
        ip = obtener_ip_local()
        if not ip:
            return "Desconocido"
        ultimo_digito = int(ip.split(".")[-1])
        nombres = {1: "Mendivelso", 2: "Tareas", 3: "Jhostin", 4: "Muñoz"}
        return nombres.get(ultimo_digito, f"Nodo-{ultimo_digito}")

    def enviar_mensaje():
        mensaje = entry.get()
        destino_ip = ip_entry.get().strip()

        if not obtener_ip_local():
            messagebox.showerror("Error de red", "No tienes una IP válida en bat0. Verifica la conexión BATMAN.")
            return

        if mensaje:
            timestamp = datetime.now().strftime("%H:%M")
            vector_clock[nombre_usuario] = vector_clock.get(nombre_usuario, 0) + 1
            mensaje_final = f"[{timestamp}] {nombre_usuario}: {mensaje} | VC: {vector_clock}"

            # Encriptar el mensaje antes de enviarlo
            mensaje_encriptado = encrypt_message(mensaje_final)

            try:
                if destino_ip:
                    ip_destino = destino_ip
                else:
                    ip_local = obtener_ip_local()
                    ip_parts = ip_local.split('.')
                    ip_destino = '.'.join(ip_parts[:3]) + '.255'

                sock.sendto(mensaje_encriptado, (ip_destino, PUERTO))

                chat_area.insert(tk.END, f"Tú: {mensaje} ({timestamp})\n")
                entry.delete(0, tk.END)

                # Añadir el mensaje a la tabla de la ventana principal
                gui.agregar_mensaje_tabla("ENVIADO", ip_destino, mensaje_final, mensaje_encriptado, vector_clock)
            except OSError as e:
                messagebox.showerror("Error", f"No se pudo enviar el mensaje:\n{e}")

    def recibir_mensajes():
        while True:
            try:
                data, addr = sock.recvfrom(BUFFER_SIZE)

                # Desencriptar el mensaje recibido
                mensaje_desencriptado = decrypt_message(data)

                if addr[0] != obtener_ip_local():
                    chat_area.insert(tk.END, f"{mensaje_desencriptado}\n")
                    # Añadir el mensaje recibido a la tabla de la ventana principal
                    gui.agregar_mensaje_tabla("RECIBIDO", addr[0], mensaje_desencriptado, data, {})
            except:
                break

    nombre_usuario = obtener_nombre()

    root_chat = tk.Toplevel()
    root_chat.title(f"Chat BATMAN - {nombre_usuario}")

    chat_area = tk.Text(root_chat, height=20, width=60)
    chat_area.pack(padx=10, pady=10)

    entry = tk.Entry(root_chat, width=60)
    entry.pack(padx=10, pady=5)

    ip_label = tk.Label(root_chat, text="IP Destino (vacío para todos):")
    ip_label.pack()
    ip_entry = tk.Entry(root_chat, width=60)
    ip_entry.pack(padx=10, pady=5)

    button_frame = tk.Frame(root_chat)
    button_frame.pack(pady=10)

    send_button = tk.Button(button_frame, text="Enviar", command=enviar_mensaje)
    send_button.pack(side=tk.LEFT, padx=5)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', PUERTO))

    threading.Thread(target=recibir_mensajes, daemon=True).start()

# ===============================
# 🏁 Main
# ===============================
if __name__ == "__main__":
    root = tk.Tk()
    gui = InterfazBATMAN(root)
    nodo = NodoBATMAN(gui)
    gui.set_nodo(nodo)
    nodo.iniciar()
    root.mainloop()