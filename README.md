# 🛰️ C3 - Chat Descentralizado con BATMAN y Control PID

Este proyecto implementa un sistema de mensajería descentralizado sobre redes ad-hoc utilizando:

- 🔁 **BATMAN** (Better Approach To Mobile Ad-hoc Networking) como protocolo de enrutamiento.
- 🔐 **Fernet** para cifrado simétrico de mensajes.
- 📊 **Controlador PID** para regular dinámicamente el flujo de mensajes.
- ⏱️ **Relojes vectoriales** para mantener el orden causal en los eventos entre nodos.
- 💬 **Interfaz gráfica tipo WhatsApp**, con integración de gráficos en tiempo real mediante `matplotlib`.

---

## 🎯 Propósito del Proyecto

Diseñar un sistema de mensajería **descentralizado**, **seguro** y **adaptable**, ideal para situaciones sin infraestructura de red como:

- Emergencias
- Ruralidad
- Entornos militares

---

## 💡 Idea General

- Comunicación en tiempo real **sin servidor central**.
- Envío **seguro y ordenado** de mensajes entre múltiples dispositivos.
- **Control autónomo** del ritmo de transmisión según condiciones de red.
- **Visualización** del estado del sistema desde la GUI.

---

## 📌 Alcance del Proyecto

- Soporte para múltiples nodos en red **ad-hoc**.
- Enrutamiento con **BATMAN**.
- Chat gráfico con **cifrado** y **relojes vectoriales**.
- Visualización de comportamiento del **PID** en tiempo real.

---

## ⚙️ Requisitos

- Python 3.8 o superior

### Bibliotecas necesarias:

```bash
pip install matplotlib cryptography
```
---

## 🔧 Configuración de Red Ad-Hoc (Ubuntu/Linux)

> ⚠️ **Importante:** Sustituye `wlp0s20f3` por tu interfaz Wi-Fi real, además asegurate de tener BATMAN instalado previamente (batctl, batman-adv).

```bash
sudo su
systemctl stop NetworkManager            # Detiene el gestor de red para evitar interferencias.
ip link set wlp0s20f3 down               # Baja la interfaz de red.
iwconfig wlp0s20f3 mode ad-hoc           # Cambia la interfaz a modo ad-hoc.
iwconfig wlp0s20f3 essid "RedBatman"     # Asigna un nombre de red (ESSID).
iwconfig wlp0s20f3 channel 1             # Establece el canal (debe ser igual en todos los nodos).
ip link set wlp0s20f3 up                 # Levanta la interfaz.
batctl if add wlp0s20f3                  # Añade la interfaz a BATMAN.
ip link set up dev wlp0s20f3             # Activa la interfaz de nuevo.
ip addr add 192.168.1.X/24 dev bat0      # Asigna una IP diferente a cada nodo.
batctl n                                 # Muestra vecinos detectados.
batctl tg                                # Muestra tabla de enrutamiento global.
```
---

## 🔁 Cómo Reproducir Esta Red Paso a Paso

### 🔌 Conéctate a la red ad-hoc

Usa los comandos anteriores para que todos los nodos estén conectados en la red **RedBatman**.

---

### 🔐 Modifica la clave de cifrado compartida

En `versionFinal.py`, cambia la siguiente línea por una clave de **32 bytes** idéntica en todos los nodos:

```python
SECRET_KEY = b'mi_clave_super_segura_de_32_bytes'
```

### 🗺️ Configura las direcciones MAC-IP de cada nodo

Cambia el diccionario `mac_ip_map` en el código por las direcciones reales de tus dispositivos:

```python
self.mac_ip_map = {
    "2c:6d:c1:f7:ec:9d": "192.168.1.4",
    "58:00:e3:6a:28:79": "192.168.1.2",
    "a0:80:69:5e:64:b5": "192.168.1.3"
}
```
Nota: Asegúrate de que las IPs coincidan con las asignadas vía ip addr.

---

### 💬 Prueba Inicial: Envío de "holas"

Al iniciar, los dispositivos envían mensajes de saludo para verificar la conexión con sus vecinos.  
Esto valida que **BATMAN** reconoce los nodos vecinos.

> Si deseas enviar mensajes personalizados, haz clic en la opción **"Abrir chat BATMAN"** en la interfaz gráfica.

---

### 🧪 Pruebas Realizadas

**Topología:** 4 nodos distribuidos a aproximadamente 15 metros de distancia entre sí.

#### ✅ Resultados:

- 🟢 Comunicación efectiva entre nodos  
- 🔐 Transmisión cifrada y sincronizada de mensajes  
- 📡 Reconocimiento dinámico de vecinos con BATMAN  
- 🔄 Control estable de la tasa de envío gracias al PID  
- 🖥️ Visualización clara en la interfaz  

---

### 🧩 Estructura del Código

- `NodoBATMAN`: Maneja recepción, envío y sincronización de mensajes con **vector clocks**  
- `PIDController`: Ajusta la frecuencia de envío para mantener el flujo estable  
- `encrypt_message / decrypt_message`: Funciones para **cifrado y descifrado** con Fernet  
- `versionFinal.py`: Script principal que conecta todos los componentes  
- `tkinter` + `matplotlib`: Interfaz gráfica tipo chat + visualización del **PID**

---

### 📈 Visualización en Tiempo Real

Incluye un gráfico embebido que muestra:

- 📉 **Error acumulado**  
- ⚙️ **Salida del PID**  
- 📥 **Tasa de recepción de mensajes**

Esto permite observar cómo se **autorregula** el sistema frente a cambios en la red.
