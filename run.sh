#!/bin/bash

# ============================================
#  any2wav - Menú Interactivo
# ============================================

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
WHITE='\033[1;37m'
DIM='\033[2m'
NC='\033[0m'

# Variables
INPUT_DIR=""
OUTPUT_DIR="./output"
FORMAT="wav"
RECURSIVE=false

# Limpiar pantalla
clear_screen() {
    clear
}

# Header ASCII
show_header() {
    echo ""
    echo -e "${CYAN}"
    cat << 'EOF'
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
EOF
    echo -e "${NC}"
}

# Mostrar configuración actual
show_config() {
    echo ""
    echo -e "${WHITE}┌─────────────────── Configuración Actual ───────────────────┐${NC}"
    echo -e "${WHITE}│${NC}"
    
    if [ -z "$INPUT_DIR" ]; then
        echo -e "${WHITE}│${NC}  📂 Carpeta entrada:  ${DIM}(no seleccionada)${NC}"
    else
        echo -e "${WHITE}│${NC}  📂 Carpeta entrada:  ${GREEN}$INPUT_DIR${NC}"
    fi
    
    echo -e "${WHITE}│${NC}  📁 Carpeta salida:   ${BLUE}$OUTPUT_DIR${NC}"
    
    if [ "$FORMAT" = "wav" ]; then
        echo -e "${WHITE}│${NC}  🎵 Formato:          ${MAGENTA}WAV${NC} (alta calidad, sin compresión)"
    else
        echo -e "${WHITE}│${NC}  🎵 Formato:          ${MAGENTA}MP3${NC} (comprimido, menor tamaño)"
    fi
    
    if [ "$RECURSIVE" = true ]; then
        echo -e "${WHITE}│${NC}  🔄 Recursivo:        ${GREEN}Sí${NC} (incluye subcarpetas)"
    else
        echo -e "${WHITE}│${NC}  🔄 Recursivo:        ${DIM}No${NC}"
    fi
    
    echo -e "${WHITE}│${NC}"
    echo -e "${WHITE}└─────────────────────────────────────────────────────────────┘${NC}"
}

# Menú principal
show_menu() {
    echo ""
    echo -e "${YELLOW}╔═══════════════════════ MENÚ ═══════════════════════╗${NC}"
    echo -e "${YELLOW}║${NC}                                                    ${YELLOW}║${NC}"
    echo -e "${YELLOW}║${NC}   ${WHITE}1.${NC} 📂  Seleccionar carpeta de entrada            ${YELLOW}║${NC}"
    echo -e "${YELLOW}║${NC}   ${WHITE}2.${NC} 📁  Cambiar carpeta de salida                 ${YELLOW}║${NC}"
    echo -e "${YELLOW}║${NC}   ${WHITE}3.${NC} 🎵  Cambiar formato (WAV/MP3)                 ${YELLOW}║${NC}"
    echo -e "${YELLOW}║${NC}   ${WHITE}4.${NC} 🔄  Toggle búsqueda recursiva                 ${YELLOW}║${NC}"
    echo -e "${YELLOW}║${NC}                                                    ${YELLOW}║${NC}"
    echo -e "${YELLOW}║${NC}   ${GREEN}5.${NC} 🚀  ${GREEN}CONVERTIR${NC}                                 ${YELLOW}║${NC}"
    echo -e "${YELLOW}║${NC}   ${CYAN}6.${NC} 👁️   Ver preview (dry-run)                    ${YELLOW}║${NC}"
    echo -e "${YELLOW}║${NC}                                                    ${YELLOW}║${NC}"
    echo -e "${YELLOW}║${NC}   ${RED}0.${NC} ❌  Salir                                     ${YELLOW}║${NC}"
    echo -e "${YELLOW}║${NC}                                                    ${YELLOW}║${NC}"
    echo -e "${YELLOW}╚════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Seleccionar carpeta de entrada
select_input() {
    echo ""
    echo -e "${CYAN}📂 Ingresá la ruta de la carpeta con archivos a convertir:${NC}"
    echo -e "${DIM}   (Podés arrastrar la carpeta acá o escribir la ruta)${NC}"
    echo ""
    read -p "   Ruta: " dir
    
    # Limpiar espacios y comillas
    dir=$(echo "$dir" | sed "s/^['\"]//;s/['\"]$//;s/^[[:space:]]*//;s/[[:space:]]*$//")
    
    if [ -d "$dir" ]; then
        INPUT_DIR="$dir"
        echo ""
        echo -e "${GREEN}✅ Carpeta seleccionada: $INPUT_DIR${NC}"
    else
        echo ""
        echo -e "${RED}❌ La carpeta no existe: $dir${NC}"
    fi
    
    sleep 1.5
}

# Cambiar carpeta de salida
select_output() {
    echo ""
    echo -e "${CYAN}📁 Ingresá la ruta de la carpeta de salida:${NC}"
    echo -e "${DIM}   (Se creará si no existe. Default: ./output)${NC}"
    echo ""
    read -p "   Ruta: " dir
    
    dir=$(echo "$dir" | sed "s/^['\"]//;s/['\"]$//;s/^[[:space:]]*//;s/[[:space:]]*$//")
    
    if [ -n "$dir" ]; then
        OUTPUT_DIR="$dir"
        echo ""
        echo -e "${GREEN}✅ Carpeta de salida: $OUTPUT_DIR${NC}"
    fi
    
    sleep 1
}

# Cambiar formato
toggle_format() {
    if [ "$FORMAT" = "wav" ]; then
        FORMAT="mp3"
        echo ""
        echo -e "${MAGENTA}🎵 Formato cambiado a: MP3${NC}"
    else
        FORMAT="wav"
        echo ""
        echo -e "${MAGENTA}🎵 Formato cambiado a: WAV${NC}"
    fi
    sleep 1
}

# Toggle recursivo
toggle_recursive() {
    if [ "$RECURSIVE" = true ]; then
        RECURSIVE=false
        echo ""
        echo -e "${BLUE}🔄 Búsqueda recursiva: DESACTIVADA${NC}"
    else
        RECURSIVE=true
        echo ""
        echo -e "${GREEN}🔄 Búsqueda recursiva: ACTIVADA${NC}"
    fi
    sleep 1
}

# Ejecutar conversión
run_conversion() {
    if [ -z "$INPUT_DIR" ]; then
        echo ""
        echo -e "${RED}❌ Primero seleccioná una carpeta de entrada (opción 1)${NC}"
        sleep 2
        return
    fi
    
    echo ""
    echo -e "${GREEN}🚀 Iniciando conversión...${NC}"
    echo ""
    sleep 1
    
    # Construir comando
    CMD="any2wav \"$INPUT_DIR\" -o \"$OUTPUT_DIR\" -f $FORMAT"
    
    if [ "$RECURSIVE" = true ]; then
        CMD="$CMD -r"
    fi
    
    # Ejecutar
    eval "$CMD"
    
    echo ""
    echo -e "${CYAN}Presioná Enter para volver al menú...${NC}"
    read
}

# Ejecutar dry-run
run_preview() {
    if [ -z "$INPUT_DIR" ]; then
        echo ""
        echo -e "${RED}❌ Primero seleccioná una carpeta de entrada (opción 1)${NC}"
        sleep 2
        return
    fi
    
    echo ""
    echo -e "${CYAN}👁️  Preview (dry-run) - No se ejecutará nada${NC}"
    echo ""
    sleep 1
    
    # Construir comando
    CMD="any2wav \"$INPUT_DIR\" -o \"$OUTPUT_DIR\" -f $FORMAT --dry-run"
    
    if [ "$RECURSIVE" = true ]; then
        CMD="$CMD -r"
    fi
    
    # Ejecutar
    eval "$CMD"
    
    echo ""
    echo -e "${CYAN}Presioná Enter para volver al menú...${NC}"
    read
}

# Activar venv si existe
activate_venv() {
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    if [ -f "$SCRIPT_DIR/venv/bin/activate" ]; then
        source "$SCRIPT_DIR/venv/bin/activate"
    else
        echo -e "${RED}❌ No se encontró el entorno virtual.${NC}"
        echo -e "${YELLOW}   Ejecutá primero: ./setup.sh${NC}"
        exit 1
    fi
}

# Main loop
main() {
    activate_venv
    
    while true; do
        clear_screen
        show_header
        show_config
        show_menu
        
        read -p "   Seleccioná una opción: " choice
        
        case $choice in
            1) select_input ;;
            2) select_output ;;
            3) toggle_format ;;
            4) toggle_recursive ;;
            5) run_conversion ;;
            6) run_preview ;;
            0) 
                clear_screen
                echo ""
                echo -e "${CYAN}👋 ¡Hasta luego!${NC}"
                echo ""
                exit 0
                ;;
            *)
                echo ""
                echo -e "${RED}❌ Opción inválida${NC}"
                sleep 1
                ;;
        esac
    done
}

# Ejecutar
main
