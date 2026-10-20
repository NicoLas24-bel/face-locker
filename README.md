# 🔒 FaceLocker

> **Seguridad biométrica facial en tiempo real para tu PC.** FaceLocker monitorea continuamente la presencia del usuario autorizado frente a la pantalla y bloquea el sistema operativo automáticamente cuando detecta una cara desconocida o ninguna cara.

---

## 📋 Tabla de Contenidos

- [¿Qué es FaceLocker?](#-qué-es-facelocker)
- [Características](#-características)
- [Cómo funciona](#-cómo-funciona)
- [Arquitectura del proyecto](#-arquitectura-del-proyecto)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Tecnologías utilizadas](#-tecnologías-utilizadas)
- [Sistemas operativos soportados](#-sistemas-operativos-soportados)

---

## 🤔 ¿Qué es FaceLocker?

FaceLocker es una aplicación de escritorio que utiliza **Inteligencia Artificial** para proteger tu sesión de PC mediante reconocimiento facial 3D. A diferencia de un simple desbloqueo por contraseña, FaceLocker **monitorea en segundo plano de forma continua**: si alguien que no eres tú se sienta frente al computador (o si te alejas), el sistema se bloquea de inmediato.

El proceso de registro es guiado y captura tu rostro desde **tres ángulos distintos** (frente, izquierda y derecha) para construir un perfil biométrico robusto resistente a spoofing básico con fotos.

---

## ✨ Características

- **🎯 Reconocimiento facial robusto** — Usa FaceNet (InceptionResnetV1 entrenado con VGGFace2) para generar embeddings de 512 dimensiones únicos por persona.
- **📐 Registro 3D multi-ángulo** — El asistente de registro solicita 3 poses (Frente, Izquierda, Derecha) capturando 5 frames por pose para mayor precisión.
- **👁️ Monitoreo continuo en segundo plano** — Corre en un hilo separado sin interrumpir tu trabajo, verificando la identidad cada 300 ms.
- **🖥️ Pantalla de privacidad** — Al detectar un rostro no autorizado, cubre la pantalla completa con una overlay negra antes de bloquear el sistema.
- **⌨️ Bloqueo por interacción física** — Si alguien toca el teclado o mueve el mouse mientras la pantalla de privacidad está activa, el SO se bloquea de inmediato.
- **🔌 Multi-entorno Linux** — Compatible con GNOME, KDE, XFCE y otros a través de múltiples comandos de bloqueo en cascada.
- **🪟 Soporte Windows** — Bloqueo nativo via `LockWorkStation()`.
- **📷 Detección automática de cámaras** — Escanea los puertos disponibles y permite seleccionar la cámara deseada.
- **⚙️ Configuración persistente** — Guarda el índice de cámara y la tolerancia en un archivo JSON local.

---

## 🔄 Cómo funciona

```
┌─────────────────────────────────────────────────────────────┐
│                      FLUJO PRINCIPAL                        │
│                                                             │
│  1. REGISTRO (primera vez)                                  │
│     Cámara → MediaPipe (pose) → MTCNN (recorte) →          │
│     FaceNet (embedding 512D) × 15 muestras →               │
│     Promedio → master_profile.npy                          │
│                                                             │
│  2. MONITOREO (en segundo plano)                            │
│     Cámara → MTCNN → FaceNet → distancia euclidiana        │
│     vs. master_profile                                      │
│     ├── distancia < umbral (0.85) → Autorizado             │
│     └── distancia >= umbral      → No autorizado            │
│              │                                              │
│              ├─ Muestra overlay de privacidad               │
│              ├─ Escucha teclado/mouse                       │
│              └─ Bloquea el SO                               │
└─────────────────────────────────────────────────────────────┘
```

### Registro guiado paso a paso

| Paso | Pose solicitada | Frames capturados |
|------|----------------|------------------|
| 1    | Frente         | 5                |
| 2    | Izquierda      | 5                |
| 3    | Derecha        | 5                |
| **Total** | **3 ángulos** | **15 embeddings → 1 perfil promedio** |

---

## 🏗️ Arquitectura del proyecto

El proyecto sigue una arquitectura en capas para mantener la separación de responsabilidades:

```
face-locker/
│
├── main.py                         # Punto de entrada
│
├── src/
│   ├── domain/                     # Lógica de IA pura
│   │   ├── face_recognizer.py      # MTCNN + FaceNet (embeddings)
│   │   └── pose_estimator.py       # MediaPipe (ángulo de cabeza)
│   │
│   ├── services/                   # Casos de uso / flujos de negocio
│   │   ├── enrollment_service.py   # Flujo completo de registro facial
│   │   └── monitoring_service.py   # Bucle de monitoreo en tiempo real
│   │
│   ├── infrastructure/             # Adaptadores al mundo exterior
│   │   ├── storage.py              # Lectura/escritura de perfil y settings
│   │   ├── lock_manager.py         # Bloqueo del SO (Linux / Windows)
│   │   ├── privacy_overlay.py      # Ventana fullscreen de privacidad
│   │   └── input_listener.py       # Escucha de teclado y mouse (pynput)
│   │
│   └── ui/                         # Interfaz gráfica
│       └── app_gui.py              # GUI con Tkinter (setup + dashboard)
│
├── data/                           # Datos locales (NO versionados)
│   ├── master_profile.npy          # Vector biométrico del usuario
│   └── settings.json               # Configuración (cámara, tolerancia)
│
├── requirements.txt
└── .gitignore
```

### Descripción de capas

| Capa | Responsabilidad |
|------|----------------|
| `domain/` | Modelos de IA: detección de pose y generación de embeddings faciales. Sin dependencias hacia otras capas. |
| `services/` | Orquesta el dominio y la infraestructura para implementar los flujos de registro y monitoreo. |
| `infrastructure/` | Todo lo que interactúa con el sistema operativo: disco, bloqueo de sesión, GUI de privacidad, periféricos. |
| `ui/` | Interfaz Tkinter que permite al usuario configurar y controlar la aplicación. |

---

## 📦 Requisitos

### Sistema
- Python **3.9 – 3.11** (recomendado 3.10)
- Cámara web funcional
- Linux o Windows

### Python (ver `requirements.txt`)

| Librería | Versión | Propósito |
|----------|---------|-----------|
| `opencv-python` | >= 4.9.0 | Captura de video y procesamiento de imagen |
| `mediapipe` | 0.10.21 | Estimación de pose y malla facial |
| `torch` | >= 2.2.0 | Backend de deep learning |
| `torchvision` | >= 0.17.0 | Transformaciones de imágenes para PyTorch |
| `facenet-pytorch` | latest | MTCNN (detección) + InceptionResnetV1 (embeddings) |
| `pynput` | latest | Escucha global de teclado y mouse |
| `numpy` | < 2.0.0 | Operaciones matriciales |

> **GPU opcional:** Si tienes una NVIDIA GPU con CUDA configurado, los modelos se cargarán automáticamente en ella para mayor velocidad. Si no, funciona perfectamente en CPU.

---

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/face-locker.git
cd face-locker
```

### 2. Crear y activar entorno virtual

```bash
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

> La primera instalación descarga los pesos del modelo FaceNet (~100 MB). Asegúrate de tener conexión a internet.

### 4. (Linux) Permisos para pynput

En algunos entornos Linux puede ser necesario agregar tu usuario al grupo `input`:

```bash
sudo usermod -aG input $USER
# Reinicia sesión para que tome efecto
```

---

## 🎮 Uso

### Ejecutar la aplicación

```bash
python main.py
```

### Primera vez — Configuración inicial

1. La app detecta que no hay perfil guardado y muestra la pantalla de **Configuración Inicial**.
2. Haz clic en **"Buscar Cámaras"** y selecciona tu cámara.
3. Haz clic en **"Iniciar Registro Facial (3D)"**.
4. Una ventana OpenCV se abrirá y te guiará:
   - **Paso 1:** Mira al frente (5 capturas automáticas)
   - **Paso 2:** Gira la cabeza a la izquierda (5 capturas)
   - **Paso 3:** Gira la cabeza a la derecha (5 capturas)
5. Al completarse, vuelves al panel principal con tu perfil guardado.

### Monitoreo activo

1. En el **Panel de Control**, presiona **"ACTIVAR MONITOREO"**.
2. El indicador cambia a verde: **"VIGILANDO EN SEGUNDO PLANO"**.
3. La app monitorea silenciosamente cada 300 ms.
4. Cuando se aleja la persona autorizada o aparece alguien distinto:
   - Aparece la **pantalla negra de privacidad**.
   - Cualquier tecla o movimiento de mouse dispara el **bloqueo del SO**.
5. Para detener, presiona **"DETENER MONITOREO"**.

### Re-registrar rostro

Si cambias de apariencia significativamente (lentes, barba, etc.) o quieres cambiar de cámara, presiona **"Re-registrar Rostro / Cambiar Cámara"** en el panel de control.

---

## 🧰 Tecnologías utilizadas

| Tecnología | Rol |
|-----------|-----|
| **Python** | Lenguaje principal |
| **FaceNet (InceptionResnetV1)** | Generación de embeddings biométricos de 512 dimensiones |
| **MTCNN** | Detección y recorte de rostros |
| **MediaPipe Face Mesh** | Estimación de pose de la cabeza (yaw/pitch) |
| **OpenCV** | Captura de video y procesamiento de frames |
| **PyTorch** | Inferencia de modelos de deep learning |
| **Tkinter** | Interfaz gráfica de usuario |
| **pynput** | Escucha global de eventos de teclado y mouse |
| **NumPy** | Cálculo de distancias euclidianas entre embeddings |

---

## 💻 Sistemas operativos soportados

| SO | Estado | Método de bloqueo |
|----|--------|------------------|
| Linux (GNOME) | Soportado | `xdg-screensaver` / `gnome-screensaver-command` / D-Bus |
| Linux (KDE / XFCE) | Soportado | `xdg-screensaver` / `loginctl lock-session` |
| Windows | Soportado | `ctypes.windll.user32.LockWorkStation()` |
| macOS | No probado | — |

---

## 📁 Datos locales (no versionados)

La carpeta `data/` contiene información biométrica personal y **no se sube al repositorio** (excluida por `.gitignore`):

- `data/master_profile.npy` — Vector matemático de 512 dimensiones del rostro del usuario.
- `data/settings.json` — Índice de cámara seleccionada y umbral de tolerancia.

Estos archivos se generan automáticamente la primera vez que completas el registro.

---

## 📄 Licencia

Este proyecto es de uso personal / educativo. Siéntete libre de adaptarlo a tus necesidades.
