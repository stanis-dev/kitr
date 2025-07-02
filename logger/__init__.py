"""
Simplified Logging Package for MetaHuman to Azure Pipeline

Provides basic logging functionality with two levels: normal and debug.
Maintains rich console output and validation tracking.

Usage:
    from logger import get_logger

    logger = get_logger('my_module')
    logger.info('Processing started')
    logger.debug('Debug information')

    # For validation
    logger.step_start('FBX Validation', 'Checking file structure')
    logger.validation_result('File exists', True, 'Found input.fbx')
"""

from .core import get_logger, setup_logging

__all__ = ['get_logger', 'setup_logging']
