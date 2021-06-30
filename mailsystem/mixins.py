from abc import ABC

from redbot.core import Config, commands
from redbot.core.bot import Red
from redbot.core.commands import Cog


class MailSystemMixin(ABC):

    def __init__(self, *nargs):
        self.config: Config
        self.bot: Red


class MetaClass(type(Cog), type(ABC)):
    pass
