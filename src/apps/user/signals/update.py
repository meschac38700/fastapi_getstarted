from sqlalchemy import Connection
from sqlalchemy.orm import Mapper

from apps.user.models import User
from core.db.signals.managers import signal_manager
from core.monitoring.logger import get_logger

_logger = get_logger(__name__)


@signal_manager.before_update(User)
def before_update(mapper: Mapper[User], connection: Connection, user: User):
    # TODO(Eliam) wip
    _logger.info(
        f"-----------> Signal User before update: {mapper}, {connection}, {user}."
    )


@signal_manager.after_update(User)
def after_update(mapper: Mapper[User], connection: Connection, user: User):
    # TODO(Eliam) wip
    _logger.info(
        f"-----------> Signal User after update: {mapper}, {connection}, {user}."
    )
