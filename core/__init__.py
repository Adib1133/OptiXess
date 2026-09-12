"""
Core engine modules for OptiScaler Per-Game Injector (Intel XeSS Edition).
"""

from core.detector import GameDetector
from core.config_generator import ConfigGenerator
from core.safety import SafetyManager, CrashWatchdog
from core.injector import Injector
from core.library import GameLibrary
from core.version_manager import VersionManager

__all__ = [
    "GameDetector",
    "ConfigGenerator",
    "SafetyManager",
    "CrashWatchdog",
    "Injector",
    "GameLibrary",
    "VersionManager"
]
