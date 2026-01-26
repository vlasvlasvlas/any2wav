"""
Detector de archivos multimedia con audio.

Usa ffprobe para analizar archivos y determinar si tienen pistas de audio extraíbles.
"""

import subprocess
import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


# Extensiones conocidas que pueden contener audio
KNOWN_EXTENSIONS = {
    # Audio
    '.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma', '.aiff', '.opus',
    # Video
    '.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpeg', '.mpg',
    # Otros
    '.3gp', '.3g2', '.mts', '.m2ts', '.ts', '.vob',
}


@dataclass
class AudioInfo:
    """Información sobre la pista de audio de un archivo."""
    has_audio: bool
    codec: Optional[str] = None
    duration_seconds: Optional[float] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    bitrate: Optional[int] = None
    error: Optional[str] = None
    
    @property
    def duration_formatted(self) -> str:
        """Duración formateada como MM:SS o HH:MM:SS."""
        if not self.duration_seconds:
            return "??:??"
        
        total_seconds = int(self.duration_seconds)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"


def check_ffprobe() -> tuple[bool, str]:
    """
    Verifica si ffprobe está disponible en el sistema.
    
    Returns:
        Tupla (disponible, mensaje)
    """
    try:
        result = subprocess.run(
            ['ffprobe', '-version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            return True, version_line
        return False, "ffprobe no responde correctamente"
    except FileNotFoundError:
        return False, "ffprobe no está instalado"
    except subprocess.TimeoutExpired:
        return False, "ffprobe no responde (timeout)"
    except Exception as e:
        return False, f"Error verificando ffprobe: {e}"


def is_supported_file(path: Path) -> bool:
    """Verifica si el archivo tiene una extensión soportada."""
    return path.suffix.lower() in KNOWN_EXTENSIONS


def get_audio_info(file_path: Path) -> AudioInfo:
    """
    Analiza un archivo y extrae información de su pista de audio.
    
    Args:
        file_path: Ruta al archivo multimedia
        
    Returns:
        AudioInfo con la información del audio o error
    """
    if not file_path.exists():
        return AudioInfo(has_audio=False, error="Archivo no encontrado")
    
    try:
        # Usar ffprobe para obtener info de streams
        result = subprocess.run(
            [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_streams',
                '-select_streams', 'a',  # Solo streams de audio
                str(file_path)
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return AudioInfo(has_audio=False, error="No se pudo analizar el archivo")
        
        data = json.loads(result.stdout)
        streams = data.get('streams', [])
        
        if not streams:
            return AudioInfo(has_audio=False, error="Sin pista de audio")
        
        # Tomar el primer stream de audio
        audio_stream = streams[0]
        
        # Extraer información
        duration = None
        if 'duration' in audio_stream:
            duration = float(audio_stream['duration'])
        
        sample_rate = None
        if 'sample_rate' in audio_stream:
            sample_rate = int(audio_stream['sample_rate'])
        
        channels = audio_stream.get('channels')
        bitrate = None
        if 'bit_rate' in audio_stream:
            bitrate = int(audio_stream['bit_rate'])
        
        return AudioInfo(
            has_audio=True,
            codec=audio_stream.get('codec_name'),
            duration_seconds=duration,
            sample_rate=sample_rate,
            channels=channels,
            bitrate=bitrate
        )
        
    except json.JSONDecodeError:
        return AudioInfo(has_audio=False, error="Respuesta inválida de ffprobe")
    except subprocess.TimeoutExpired:
        return AudioInfo(has_audio=False, error="Timeout analizando archivo")
    except Exception as e:
        return AudioInfo(has_audio=False, error=f"Error: {e}")


def find_media_files(directory: Path, recursive: bool = False) -> list[Path]:
    """
    Busca archivos multimedia en un directorio.
    
    Args:
        directory: Directorio a buscar
        recursive: Si buscar en subdirectorios
        
    Returns:
        Lista de paths a archivos multimedia
    """
    if not directory.is_dir():
        return []
    
    files = []
    pattern = '**/*' if recursive else '*'
    
    for path in directory.glob(pattern):
        if path.is_file() and is_supported_file(path):
            files.append(path)
    
    return sorted(files)
