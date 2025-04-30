from apps.user.models import User
from core.db.signals.managers import signal_manager
from core.monitoring.logger import get_logger

_logger = get_logger(__name__)


@signal_manager.before_update(User)
def before_update(*args, **kwargs):
    # TODO(Eliam) wip
    _logger.info(f"-----------> Signal User before update: {args}, {kwargs}")


@signal_manager.after_update(User)
def after_update(*args, **kwargs):
    # TODO(Eliam) wip
    _logger.info(f"-----------> Signal User after update: {args}, {kwargs}")
