# 🛰️ C3 - Chat Descentralizado con BATMAN y Control PID

Este proyecto implementa un sistema de mensajería descentralizado sobre redes ad-hoc utilizando:

- 🔁 **BATMAN** (Better Approach To Mobile Ad-hoc Networking) como protocolo de enrutamiento.
- 🔐 **Fernet** para cifrado simétrico de mensajes.
- 📊 **Controlador PID** para regular dinámicamente el flujo de mensajes.
- ⏱️ **Relojes vectoriales** para mantener el orden causal en los eventos entre nodos.
- 💬 Interfaz gráfica tipo WhatsApp, con integración de gráficos en tiempo real mediante matplotlib.

---

## 🎯 Propósito del Proyecto

Diseñar un sistema de mensajería descentralizado, seguro y adaptable, ideal para situaciones sin infraestructura de red (emergencias, ruralidad, entornos militares).

---

## 💡 Idea General

- Comunicación en tiempo real sin servidor central.
- Envío seguro y ordenado de mensajes entre múltiples dispositivos.
- Control autónomo del ritmo de transmisión según condiciones de red.
- Visualización del estado del sistema desde la GUI.

---

## 📌 Alcance del Proyecto

- Soporte para múltiples nodos en red ad-hoc.
- Enrutamiento con BATMAN.
- Chat gráfico con cifrado y relojes vectoriales.
- Visualización de comportamiento del PID en tiempo real.

---

## ⚙️ Requisitos

- Python 3.8 o superior
- Bibliotecas necesarias:
  ```bash
  pip install matplotlib cryptography

---

## 🔧 Configuración de Red Ad-Hoc (Ubuntu/Linux)

Sustituye `wlp0s20f3` por tu interfaz Wi-Fi real.

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

**Cambia wlp0s20f3 por la interfaz de red que posee tu computador**

Nota: BATMAN debe estar instalado previamente (batctl, batman-adv).
