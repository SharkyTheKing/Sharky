from typing import Optional

import discord
from redbot.core import commands, checks
from redbot.core.utils.chat_formatting import box, pagify

from .mixins import MailSystemMixin


class ModCommands(MailSystemMixin):
    """
    Mod commands for guild staffs
    """

    @commands.group(name="mailset")
    async def mailsystem_settings(self, ctx: commands.Context):
        pass

    @checks.mod_or_permissions(manage_channels=True)
    @mailsystem_settings.group(name="mod")
    async def moderator_commands(self, ctx: commands.Context):
        """
        Moderator commands for Mailset
        """
        pass
