
# C3 - Chat Descentralizado con BATMAN y Control PID

Este proyecto implementa un sistema de chat descentralizado sobre redes ad-hoc, utilizando el protocolo **BATMAN** (Better Approach To Mobile Ad-hoc Networking), sincronización de eventos mediante **vector clocks**, y control de flujo de mensajes con un **controlador PID**. También incluye una interfaz gráfica tipo WhatsApp construida en **Tkinter**, e integración de gráficas en tiempo real con **matplotlib**.

## Características

- 🔐 Encriptación de mensajes con Fernet y clave secreta compartida.
- 📡 Comunicación descentralizada sin servidor central.
- 📈 Ajuste dinámico de la tasa de envío con un controlador PID.
- ⏱️ Sincronización entre nodos mediante relojes vectoriales.
- 🖥️ Interfaz gráfica intuitiva estilo mensajería instantánea.
- 📊 Gráfica en tiempo real del comportamiento del PID.

## Requisitos

- Python 3.8 o superior
- Bibliotecas:
  - `tkinter`
  - `matplotlib`
  - `cryptography`

Puedes instalar las dependencias necesarias con:

```bash
pip install matplotlib cryptography
```

> `tkinter` viene preinstalado con la mayoría de las distribuciones de Python. Si no lo tienes, consulta la documentación de tu sistema operativo.

## Configuración de Red Ad-Hoc (Ubuntu/Linux)

Para establecer la red ad-hoc entre nodos, se deben ejecutar los siguientes comandos en una terminal con privilegios de superusuario. Asegúrate de sustituir `wlp0s20f3` por el nombre real de tu interfaz Wi-Fi.

```bash
sudo su
systemctl stop NetworkManager
ip link set wlp0s20f3 down
iwconfig wlp0s20f3 mode ad-hoc
iwconfig wlp0s20f3 essid "RedBatman"
iwconfig wlp0s20f3 channel 1
ip link set wlp0s20f3 up
batctl if add wlp0s20f3
ip link set up dev wlp0s20f3 
ip addr add 192.168.1.3/24 dev bat0
batctl n
batctl tg
```

> Estos pasos deben realizarse en **Ubuntu o cualquier distribución basada en Linux**. El protocolo BATMAN debe estar previamente instalado (`batctl`, `batman-adv`).

## Ejecución

1. Conéctate a la red ad-hoc como se indica en la sección anterior.
2. Modifica la clave compartida en `versionFinal.py` para que sea la misma en todos los nodos:
   ```python
   SECRET_KEY = b'tu_clave_secreta_compartida_32_bytes_longitud_'
   ```
3. Ejecuta el script:

```bash
python versionFinal.py
```

## Estructura del código

- `NodoBATMAN`: Lógica de comunicación y sincronización del nodo.
- `PIDController`: Ajusta el intervalo de envío según tasa de recepción.
- `encrypt_message / decrypt_message`: Encriptación y desencriptación de los mensajes.
- Interfaz gráfica: Chat descentralizado con diseño tipo WhatsApp + gráficos de PID.

## Autor

Andres Moreno, Santiago Mendivelso, Juan Muñoz y Leonardo (proyecto universitario de sistemas distribuidos y redes ad-hoc).

