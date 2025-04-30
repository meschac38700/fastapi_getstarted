from core.db.signals.managers.base import get_signal_manager

signal_manager = get_signal_manager()

__all__ = [
    "signal_manager",
]
