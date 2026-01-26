"""
Conversor de audio usando FFmpeg.

Wrapper sobre ffmpeg para convertir archivos multimedia a formatos de audio.
"""

import subprocess
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from enum import Enum


class OutputFormat(Enum):
    """Formatos de salida soportados."""
    WAV = "wav"
    MP3 = "mp3"
    
    @property
    def extension(self) -> str:
        return f".{self.value}"
    
    @classmethod
    def from_string(cls, value: str) -> 'OutputFormat':
        """Crea un OutputFormat desde un string."""
        value = value.lower().strip()
        for fmt in cls:
            if fmt.value == value:
                return fmt
        raise ValueError(f"Formato no soportado: {value}. Usa: wav, mp3")


@dataclass
class ConversionResult:
    """Resultado de una conversión."""
    success: bool
    input_path: Path
    output_path: Optional[Path] = None
    output_size_bytes: Optional[int] = None
    error: Optional[str] = None
    skipped: bool = False
    skip_reason: Optional[str] = None
    
    @property
    def output_size_formatted(self) -> str:
        """Tamaño formateado en KB o MB."""
        if not self.output_size_bytes:
            return "? KB"
        
        if self.output_size_bytes < 1024 * 1024:
            return f"{self.output_size_bytes / 1024:.1f} KB"
        return f"{self.output_size_bytes / (1024 * 1024):.1f} MB"


def check_ffmpeg() -> tuple[bool, str]:
    """
    Verifica si ffmpeg está disponible en el sistema.
    
    Returns:
        Tupla (disponible, mensaje)
    """
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            return True, version_line
        return False, "ffmpeg no responde correctamente"
    except FileNotFoundError:
        return False, "ffmpeg no está instalado"
    except subprocess.TimeoutExpired:
        return False, "ffmpeg no responde (timeout)"
    except Exception as e:
        return False, f"Error verificando ffmpeg: {e}"


def get_output_path(
    input_path: Path,
    output_dir: Path,
    output_format: OutputFormat
) -> Path:
    """
    Genera la ruta de salida para un archivo.
    
    La estructura es: output_dir/formato/nombre_archivo.extension
    
    Args:
        input_path: Archivo de entrada
        output_dir: Directorio base de salida
        output_format: Formato de salida
        
    Returns:
        Path del archivo de salida
    """
    format_dir = output_dir / output_format.value
    format_dir.mkdir(parents=True, exist_ok=True)
    
    output_name = input_path.stem + output_format.extension
    return format_dir / output_name


def convert_file(
    input_path: Path,
    output_path: Path,
    output_format: OutputFormat,
    overwrite: bool = False,
    bitrate: str = "192k",  # Para MP3
    sample_rate: Optional[int] = None,
) -> ConversionResult:
    """
    Convierte un archivo multimedia a audio.
    
    Args:
        input_path: Archivo de entrada
        output_path: Archivo de salida
        output_format: Formato de salida
        overwrite: Si sobrescribir archivos existentes
        bitrate: Bitrate para MP3 (ej: "192k", "320k")
        sample_rate: Sample rate en Hz (None = mantener original)
        
    Returns:
        ConversionResult con el resultado de la conversión
    """
    # Verificar si ya existe
    if output_path.exists() and not overwrite:
        return ConversionResult(
            success=True,
            input_path=input_path,
            output_path=output_path,
            output_size_bytes=output_path.stat().st_size,
            skipped=True,
            skip_reason="Ya existe"
        )
    
    # Asegurar que el directorio de salida existe
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Construir comando ffmpeg
    cmd = [
        'ffmpeg',
        '-y' if overwrite else '-n',  # Sobrescribir o no
        '-i', str(input_path),
        '-vn',  # Sin video
    ]
    
    # Configurar según formato de salida
    if output_format == OutputFormat.MP3:
        cmd.extend([
            '-acodec', 'libmp3lame',
            '-b:a', bitrate,
        ])
    elif output_format == OutputFormat.WAV:
        cmd.extend([
            '-acodec', 'pcm_s16le',  # WAV estándar 16-bit
        ])
    
    # Sample rate opcional
    if sample_rate:
        cmd.extend(['-ar', str(sample_rate)])
    
    cmd.append(str(output_path))
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minutos max por archivo
        )
        
        if result.returncode != 0:
            # Extraer mensaje de error útil
            error_lines = result.stderr.split('\n')
            error_msg = next(
                (line for line in reversed(error_lines) if line.strip()),
                "Error desconocido"
            )
            return ConversionResult(
                success=False,
                input_path=input_path,
                error=error_msg[:100]  # Limitar longitud
            )
        
        # Verificar que el archivo se creó
        if not output_path.exists():
            return ConversionResult(
                success=False,
                input_path=input_path,
                error="El archivo de salida no se creó"
            )
        
        return ConversionResult(
            success=True,
            input_path=input_path,
            output_path=output_path,
            output_size_bytes=output_path.stat().st_size
        )
        
    except subprocess.TimeoutExpired:
        return ConversionResult(
            success=False,
            input_path=input_path,
            error="Timeout (archivo muy grande o proceso bloqueado)"
        )
    except Exception as e:
        return ConversionResult(
            success=False,
            input_path=input_path,
            error=str(e)[:100]
        )
