```
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║      █████╗ ███╗  ██╗██╗   ██╗██████╗ ██╗    ██╗ █████╗ ██╗   ██╗ ║
║     ██╔══██╗████╗ ██║╚██╗ ██╔╝╚════██╗██║    ██║██╔══██╗██║   ██║ ║
║     ███████║██╔██╗██║ ╚████╔╝  █████╔╝██║ █╗ ██║███████║██║   ██║ ║
║     ██╔══██║██║╚████║  ╚██╔╝  ██╔═══╝ ██║███╗██║██╔══██║╚██╗ ██╔╝ ║
║     ██║  ██║██║ ╚███║   ██║   ███████╗╚███╔███╔╝██║  ██║ ╚████╔╝  ║
║     ╚═╝  ╚═╝╚═╝  ╚══╝   ╚═╝   ╚══════╝ ╚══╝╚══╝ ╚═╝  ╚═╝  ╚═══╝   ║
║                                                                   ║
║               Conversor Universal de Audio                        ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
```

> Extrae audio de cualquier archivo multimedia y conviértelo a WAV o MP3

---

## ✨ Características

| Feature | Descripción |
|---------|-------------|
| 🎵 **Multi-formato entrada** | MP3, MP4, M4A, MKV, AVI, FLAC, OGG, WEBM, y más |
| 🔊 **Formatos salida** | WAV, MP3 |
| ⏩ **Skip inteligente** | No reprocesa archivos que ya existen |
| 📊 **Progreso visual** | Barras de progreso, contadores, estadísticas |
| 📝 **Logging completo** | Registro de ejecución y conversiones en JSON |
| 🖥️ **Menú interactivo** | Interfaz ASCII visual con `./run.sh` |

---

## 📋 Requisitos

- **Python 3.8+**
- **FFmpeg** instalado en el sistema

### Instalar FFmpeg

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows - Descargar de https://ffmpeg.org/download.html
```

---

## 🚀 Instalación

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/any2wav.git
cd any2wav

# Ejecutar setup (crea venv e instala dependencias)
chmod +x setup.sh
./setup.sh
```

---

## 📖 Uso

### Opción 1: Menú Interactivo (recomendado)

```bash
./run.sh
```

Abre un menú visual donde podés:
- Seleccionar carpeta de entrada
- Elegir formato de salida (WAV/MP3)
- Activar búsqueda recursiva
- Ver preview antes de convertir

### Opción 2: Línea de Comandos

```bash
# Activar entorno virtual
source venv/bin/activate

# Convertir todos los archivos a WAV
any2wav ./mi_carpeta -f wav

# Convertir a MP3
any2wav ./mi_carpeta -f mp3

# Buscar en subcarpetas
any2wav ./mi_carpeta -f wav -r

# Especificar carpeta de salida
any2wav ./mi_carpeta -o ./converted -f wav

# Ver qué haría sin ejecutar (dry-run)
any2wav ./mi_carpeta --dry-run

# Ver ayuda
any2wav --help
```

---

## 📁 Estructura de Salida

```
output/
├── wav/
│   ├── cancion1.wav
│   └── video_audio.wav
├── mp3/
│   └── cancion1.mp3
├── any2wav.log         # Log de ejecución
└── conversions.json    # Registro de conversiones
```

---

## 📊 Display Visual

```
╔══════════════════════════════════════════════════╗
║       A N Y 2 W A V                              ║
║       Conversor Universal de Audio               ║
╚══════════════════════════════════════════════════╝

ℹ️  Buscando archivos multimedia en ./input...

┌─────────────────────┬───────────────────┐
│ Configuración       │ Valor             │
├─────────────────────┼───────────────────┤
│ 📂 Carpeta entrada  │ ./input           │
│ 📁 Carpeta salida   │ ./output/wav      │
│ 🎵 Formato salida   │ WAV               │
│ 📊 Archivos         │ 5                 │
└─────────────────────┴───────────────────┘

Convirtiendo a WAV... ━━━━━━━━━━ 100% 0:00:12

✅ cancion.mp3 → wav (12.5 MB, 3:45)
✅ video.mp4 → wav (8.2 MB, 2:30)
⏩ audio.wav → ya existe, saltando
⏭️  silent.mp4 - Sin pista de audio

✅ ¡Conversión completada!
```

---

## 📝 Logs

### Log de ejecución (`any2wav.log`)
```
2024-01-26 10:30:15 | INFO     | === Iniciando conversión ===
2024-01-26 10:30:15 | INFO     | Input: ./input
2024-01-26 10:30:15 | INFO     | OK: cancion.mp3 -> ./output/wav/cancion.wav
```

### Registro de conversiones (`conversions.json`)
```json
{
  "last_updated": "2024-01-26T10:30:45",
  "total_conversions": 3,
  "conversions": [
    {
      "timestamp": "2024-01-26T10:30:20",
      "input_file": "./input/cancion.mp3",
      "output_file": "./output/wav/cancion.wav",
      "success": true
    }
  ]
}
```

---

## 🗂️ Estructura del Proyecto

```
any2wav/
├── any2wav/
│   ├── __init__.py      # Package version
│   ├── __main__.py      # python -m entry point
│   ├── cli.py           # CLI con Rich UI
│   ├── converter.py     # FFmpeg wrapper
│   ├── detector.py      # FFprobe wrapper
│   └── logger.py        # Dual logging
├── run.sh               # Menú interactivo
├── setup.sh             # Setup venv + deps
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## 📄 Licencia

MIT
