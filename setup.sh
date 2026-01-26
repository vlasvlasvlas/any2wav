#!/bin/bash

# ============================================
#  any2wav - Setup Script
# ============================================
#  Este script configura el entorno virtual
#  e instala todas las dependencias necesarias.
# ============================================

set -e

# Colores para mensajes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         any2wav - Configuración          ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
echo ""

# Verificar Python
echo -e "${YELLOW}[1/4]${NC} Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 no está instalado${NC}"
    echo "   Instalalo desde https://python.org"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✅ $PYTHON_VERSION${NC}"

# Verificar FFmpeg
echo ""
echo -e "${YELLOW}[2/4]${NC} Verificando FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${RED}❌ FFmpeg no está instalado${NC}"
    echo ""
    echo "   Instalalo según tu sistema operativo:"
    echo ""
    echo "   macOS:        brew install ffmpeg"
    echo "   Ubuntu/Debian: sudo apt install ffmpeg"
    echo "   Windows:      Descargar de https://ffmpeg.org/download.html"
    echo ""
    exit 1
fi
FFMPEG_VERSION=$(ffmpeg -version | head -n1)
echo -e "${GREEN}✅ $FFMPEG_VERSION${NC}"

# Crear entorno virtual
echo ""
echo -e "${YELLOW}[3/4]${NC} Creando entorno virtual..."
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠️  El directorio venv ya existe, usando el existente${NC}"
else
    python3 -m venv venv
    echo -e "${GREEN}✅ Entorno virtual creado en ./venv${NC}"
fi

# Instalar dependencias
echo ""
echo -e "${YELLOW}[4/4]${NC} Instalando dependencias..."
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
pip install -e . -q
echo -e "${GREEN}✅ Dependencias instaladas${NC}"

# Mensaje final
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║       ✅ Configuración completada        ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
echo ""
echo "Para usar any2wav:"
echo ""
echo -e "  ${BLUE}1.${NC} Activar el entorno virtual:"
echo -e "     ${YELLOW}source venv/bin/activate${NC}"
echo ""
echo -e "  ${BLUE}2.${NC} Convertir archivos a WAV:"
echo -e "     ${YELLOW}any2wav ./mi_carpeta -f wav${NC}"
echo ""
echo -e "  ${BLUE}3.${NC} Convertir archivos a MP3:"
echo -e "     ${YELLOW}any2wav ./mi_carpeta -f mp3${NC}"
echo ""
echo -e "  ${BLUE}4.${NC} Ver ayuda completa:"
echo -e "     ${YELLOW}any2wav --help${NC}"
echo ""
