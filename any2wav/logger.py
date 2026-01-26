"""
Sistema de logging para any2wav.

Proporciona:
1. Log de ejecución (archivo .log) - para debug y seguimiento
2. Registro de conversiones (JSON) - historial de archivos procesados
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict


@dataclass
class ConversionRecord:
    """Registro de una conversión individual."""
    timestamp: str
    input_file: str
    output_file: Optional[str]
    input_format: str
    output_format: str
    success: bool
    skipped: bool
    error: Optional[str]
    size_bytes: Optional[int]
    duration_seconds: Optional[float]


class ConversionLogger:
    """Logger para registrar conversiones en archivo JSON."""
    
    def __init__(self, output_dir: Path):
        """
        Inicializa el logger de conversiones.
        
        Args:
            output_dir: Directorio donde guardar conversions.json
        """
        self.output_dir = output_dir
        self.log_file = output_dir / "conversions.json"
        self.records: list[dict] = []
        
        # Cargar registros existentes si hay
        self._load_existing()
    
    def _load_existing(self):
        """Carga registros existentes del archivo JSON."""
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.records = data.get('conversions', [])
            except (json.JSONDecodeError, IOError):
                self.records = []
    
    def _save(self):
        """Guarda los registros al archivo JSON."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        data = {
            'last_updated': datetime.now().isoformat(),
            'total_conversions': len(self.records),
            'conversions': self.records
        }
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def log_conversion(self, record: ConversionRecord):
        """
        Registra una conversión.
        
        Args:
            record: Registro de la conversión
        """
        self.records.append(asdict(record))
        self._save()
    
    def get_converted_files(self) -> set[str]:
        """
        Obtiene el set de archivos de entrada ya convertidos.
        
        Returns:
            Set de paths de archivos de entrada ya procesados exitosamente
        """
        return {
            r['input_file'] 
            for r in self.records 
            if r.get('success') and not r.get('skipped')
        }


def setup_execution_logger(output_dir: Path, verbose: bool = False) -> logging.Logger:
    """
    Configura el logger de ejecución.
    
    Args:
        output_dir: Directorio para el archivo .log
        verbose: Si mostrar logs debug en consola
        
    Returns:
        Logger configurado
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger('any2wav')
    logger.setLevel(logging.DEBUG)
    
    # Limpiar handlers existentes
    logger.handlers.clear()
    
    # Handler para archivo
    log_file = output_dir / "any2wav.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Handler para consola (solo si verbose)
    if verbose:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    return logger
