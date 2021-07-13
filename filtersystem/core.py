import re
from typing import Optional

import discord
from redbot.core import Config, checks, commands
from redbot.core.utils.chat_formatting import box, humanize_list, pagify

from .auditlog import AuditLogging, PrivateLogEntry, PublicLogEntry
from .mixins import MetaClass
from .staffcommands import StaffCommands

BASECOG = getattr(commands, "Cog", object)

DEF_GUILD = {
    "filter_log": None,
    "command_log": None,
    "word_filter": [],
    "exact_filter": [],
    "whitelist": [],
}

DEF_CHANNEL = {"word_filter": [], "exact_filter": [], "whitelist": []}

mixinargs = (AuditLogging, StaffCommands, BASECOG)


class FilterSystem(*mixinargs, metaclass=MetaClass):
    """
    FilterSystem an alternative to core's filter.

    This is an advanced filtersystem, please use with caution.
    """

    __version__ = "0.0.1"
    __author__ = ["SharkyTheKing", "Bakersbakebread"]

    def __init__(self, bot):
        self.bot = bot
        self.added_color = discord.Color.green()
        self.removed_color = discord.Color.dark_red()
        self.config = Config.get_conf(self, identifier=223391425302102016)
        self.config.register_guild(**DEF_GUILD)
        self.config.register_channel(**DEF_CHANNEL)
        self.regex_cache = {}
        # set a task to cache regex

    def format_help_for_context(self, ctx: commands.Context) -> str:
        context = super().format_help_for_context(ctx)
        authors = humanize_list(self.__author__)
        return f"{context}\n\nAuthors: {authors}\nVersion: {self.__version__}"

    async def word_count_validation(self, ctx, word: str) -> bool:
        if len(word) <= 4:
            confirmation_message = await self.yes_or_no(
                ctx, f"{word} has 4 or less characters, are you sure you want to add?"
            )
            if not confirmation_message:
                await ctx.send(f"{word} won't be added.")
                return False

    async def truncate_message_content(self, message: discord.Message) -> str:
        if len(message.content.split()) > 25:
            return message.content[:120] + "... (shortened)"
        # probably a check here for total length too? I dno
        else:
            return message.content

    @staticmethod  # Thank you zixy
    def split_len(seq, length):
        """
        Splits a sequence into n sized pieces
        stolen from stacktrace
        """
        return [seq[i : i + length] for i in range(0, len(seq), length)]
