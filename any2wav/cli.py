"""
CLI principal de any2wav.

Interfaz de línea de comandos con display visual usando Rich.
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.table import Table
from rich import box

from . import __version__
from .detector import check_ffprobe, find_media_files, get_audio_info, is_supported_file
from .converter import check_ffmpeg, convert_file, get_output_path, OutputFormat, ConversionResult
from .logger import setup_execution_logger, ConversionLogger, ConversionRecord


console = Console()


def print_header():
    """Muestra el header de la aplicación."""
    console.print()
    console.print(Panel.fit(
        "[bold cyan]any2wav[/bold cyan] - Conversor Universal de Audio\n"
        f"[dim]v{__version__}[/dim]",
        border_style="cyan"
    ))
    console.print()


def print_error(message: str):
    """Muestra un mensaje de error."""
    console.print(f"[red]❌ {message}[/red]")


def print_warning(message: str):
    """Muestra un mensaje de advertencia."""
    console.print(f"[yellow]⚠️  {message}[/yellow]")


def print_success(message: str):
    """Muestra un mensaje de éxito."""
    console.print(f"[green]✅ {message}[/green]")


def print_info(message: str):
    """Muestra un mensaje informativo."""
    console.print(f"[blue]ℹ️  {message}[/blue]")


def print_skip(message: str):
    """Muestra un mensaje de archivo saltado."""
    console.print(f"[dim]⏩ {message}[/dim]")


def check_dependencies() -> bool:
    """
    Verifica que ffmpeg y ffprobe estén disponibles.
    
    Returns:
        True si todo está OK, False si falta algo
    """
    # Verificar ffmpeg
    ffmpeg_ok, ffmpeg_msg = check_ffmpeg()
    if not ffmpeg_ok:
        print_error("FFmpeg no está instalado")
        console.print()
        console.print("[yellow]Instalá FFmpeg según tu sistema operativo:[/yellow]")
        console.print()
        console.print("  [cyan]macOS:[/cyan]         brew install ffmpeg")
        console.print("  [cyan]Ubuntu/Debian:[/cyan] sudo apt install ffmpeg")
        console.print("  [cyan]Windows:[/cyan]       Descargar de https://ffmpeg.org/download.html")
        console.print()
        return False
    
    # Verificar ffprobe
    ffprobe_ok, ffprobe_msg = check_ffprobe()
    if not ffprobe_ok:
        print_error("FFprobe no está disponible (viene con FFmpeg)")
        return False
    
    return True


def show_summary(
    input_dir: Path,
    files: list[Path],
    output_format: OutputFormat,
    output_dir: Path
):
    """Muestra un resumen antes de procesar."""
    # Contar formatos
    format_counts: dict[str, int] = {}
    for f in files:
        ext = f.suffix.lower()
        format_counts[ext] = format_counts.get(ext, 0) + 1
    
    # Crear tabla de resumen
    table = Table(box=box.ROUNDED, border_style="cyan")
    table.add_column("Configuración", style="bold")
    table.add_column("Valor")
    
    table.add_row("📂 Carpeta entrada", str(input_dir))
    table.add_row("📁 Carpeta salida", str(output_dir / output_format.value))
    table.add_row("🎵 Formato salida", output_format.value.upper())
    table.add_row("📊 Archivos encontrados", str(len(files)))
    
    # Mostrar desglose por formato
    if format_counts:
        formats_str = ", ".join(f"{ext}: {count}" for ext, count in sorted(format_counts.items()))
        table.add_row("📋 Formatos entrada", formats_str)
    
    console.print(table)
    console.print()


def process_files(
    files: list[Path],
    output_dir: Path,
    output_format: OutputFormat,
    overwrite: bool,
    dry_run: bool,
    logger,
    conversion_logger: ConversionLogger
) -> dict:
    """
    Procesa todos los archivos.
    
    Returns:
        Diccionario con estadísticas
    """
    stats = {
        'total': len(files),
        'converted': 0,
        'skipped': 0,
        'errors': 0,
        'no_audio': 0
    }
    
    if dry_run:
        print_info("Modo dry-run: mostrando qué se haría sin ejecutar")
        console.print()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        
        task = progress.add_task(
            f"[cyan]Convirtiendo a {output_format.value.upper()}...",
            total=len(files)
        )
        
        for file_path in files:
            # Obtener info del archivo
            audio_info = get_audio_info(file_path)
            
            if not audio_info.has_audio:
                stats['no_audio'] += 1
                progress.console.print(
                    f"[yellow]⏭️  {file_path.name}[/yellow] - Sin pista de audio"
                )
                logger.info(f"SKIP (no audio): {file_path}")
                progress.advance(task)
                continue
            
            # Calcular ruta de salida
            output_path = get_output_path(file_path, output_dir, output_format)
            
            if dry_run:
                if output_path.exists() and not overwrite:
                    progress.console.print(
                        f"[dim]⏩ {file_path.name} → ya existe, se saltaría[/dim]"
                    )
                else:
                    progress.console.print(
                        f"[green]➡️  {file_path.name}[/green] → {output_path.name}"
                    )
                progress.advance(task)
                continue
            
            # Convertir
            result = convert_file(
                file_path,
                output_path,
                output_format,
                overwrite=overwrite
            )
            
            # Registrar en log
            record = ConversionRecord(
                timestamp=datetime.now().isoformat(),
                input_file=str(file_path),
                output_file=str(result.output_path) if result.output_path else None,
                input_format=file_path.suffix.lower(),
                output_format=output_format.value,
                success=result.success,
                skipped=result.skipped,
                error=result.error,
                size_bytes=result.output_size_bytes,
                duration_seconds=audio_info.duration_seconds
            )
            conversion_logger.log_conversion(record)
            
            # Mostrar resultado
            if result.skipped:
                stats['skipped'] += 1
                progress.console.print(
                    f"[dim]⏩ {file_path.name} → ya existe, saltando[/dim]"
                )
                logger.info(f"SKIP (exists): {file_path}")
            elif result.success:
                stats['converted'] += 1
                size_str = result.output_size_formatted
                duration_str = audio_info.duration_formatted
                progress.console.print(
                    f"[green]✅ {file_path.name}[/green] → {output_format.value} "
                    f"[dim]({size_str}, {duration_str})[/dim]"
                )
                logger.info(f"OK: {file_path} -> {result.output_path}")
            else:
                stats['errors'] += 1
                progress.console.print(
                    f"[red]❌ {file_path.name}[/red] - {result.error}"
                )
                logger.error(f"ERROR: {file_path} - {result.error}")
            
            progress.advance(task)
    
    return stats


def show_final_stats(stats: dict, dry_run: bool):
    """Muestra las estadísticas finales."""
    console.print()
    
    table = Table(title="📊 Resumen", box=box.ROUNDED, border_style="green")
    table.add_column("Métrica", style="bold")
    table.add_column("Cantidad", justify="right")
    
    table.add_row("Total archivos", str(stats['total']))
    
    if not dry_run:
        table.add_row("[green]Convertidos[/green]", str(stats['converted']))
        table.add_row("[dim]Saltados (ya existían)[/dim]", str(stats['skipped']))
        table.add_row("[yellow]Sin audio[/yellow]", str(stats['no_audio']))
        table.add_row("[red]Errores[/red]", str(stats['errors']))
    
    console.print(table)
    console.print()


def main():
    """Entry point principal."""
    parser = argparse.ArgumentParser(
        prog='any2wav',
        description='Conversor universal de audio - extrae audio de cualquier archivo multimedia',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  any2wav ./videos -f wav          Convertir a WAV
  any2wav ./musica -f mp3          Convertir a MP3
  any2wav ./media -f wav -r        Buscar en subcarpetas
  any2wav ./input --dry-run        Ver qué haría sin ejecutar
        """
    )
    
    parser.add_argument(
        'input_dir',
        type=Path,
        help='Carpeta con archivos a convertir'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=Path,
        default=Path('./out'),
        help='Carpeta de salida (default: ./out)'
    )
    
    parser.add_argument(
        '-f', '--format',
        type=str,
        default='wav',
        choices=['wav', 'mp3'],
        help='Formato de salida: wav, mp3 (default: wav)'
    )
    
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Buscar en subcarpetas'
    )
    
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Sobrescribir archivos existentes'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Mostrar qué haría sin ejecutar'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Mostrar información de debug'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    
    args = parser.parse_args()
    
    # Mostrar header
    print_header()
    
    # Verificar dependencias
    if not check_dependencies():
        sys.exit(1)
    
    # Verificar directorio de entrada
    if not args.input_dir.exists():
        print_error(f"La carpeta no existe: {args.input_dir}")
        sys.exit(1)
    
    if not args.input_dir.is_dir():
        print_error(f"No es una carpeta: {args.input_dir}")
        sys.exit(1)
    
    # Parsear formato
    try:
        output_format = OutputFormat.from_string(args.format)
    except ValueError as e:
        print_error(str(e))
        sys.exit(1)
    
    # Buscar archivos
    print_info(f"Buscando archivos multimedia en {args.input_dir}...")
    files = find_media_files(args.input_dir, recursive=args.recursive)
    
    if not files:
        print_warning(f"No se encontraron archivos multimedia en {args.input_dir}")
        console.print()
        console.print("[dim]Formatos soportados: mp3, mp4, m4a, mkv, avi, wav, flac, ogg, webm, etc.[/dim]")
        sys.exit(0)
    
    console.print()
    
    # Configurar logging
    logger = setup_execution_logger(args.output, verbose=args.verbose)
    conversion_logger = ConversionLogger(args.output)
    
    logger.info(f"=== Iniciando conversión ===")
    logger.info(f"Input: {args.input_dir}")
    logger.info(f"Output: {args.output}")
    logger.info(f"Format: {output_format.value}")
    logger.info(f"Files found: {len(files)}")
    
    # Mostrar resumen
    show_summary(args.input_dir, files, output_format, args.output)
    
    # Procesar
    stats = process_files(
        files,
        args.output,
        output_format,
        args.overwrite,
        args.dry_run,
        logger,
        conversion_logger
    )
    
    # Mostrar estadísticas finales
    show_final_stats(stats, args.dry_run)
    
    logger.info(f"=== Conversión completada ===")
    logger.info(f"Converted: {stats['converted']}, Skipped: {stats['skipped']}, Errors: {stats['errors']}")
    
    # Exit code según errores
    if stats['errors'] > 0:
        sys.exit(1)
    
    print_success("¡Conversión completada!")


if __name__ == '__main__':
    main()
