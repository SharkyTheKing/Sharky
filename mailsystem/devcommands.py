import asyncio
from typing import Optional

import discord
from redbot.core import commands, checks
from redbot.core.utils.chat_formatting import box, pagify

from .mixins import MailSystemMixin
from .embedmodel import EmbedSettings


class DevCommands(MailSystemMixin):
    """
    Dev Commands for bot owner and guild staff
    """

    @commands.group(name="mailset")
    async def mailsystem_settings(self, ctx: commands.Context):
        pass

    @checks.mod_or_permissions(manage_guild=True)
    @mailsystem_settings.group(name="dev")
    async def developer_commands(self, ctx: commands.Context):
        """
        Dev commands for Mailset
        """
        pass

    @checks.is_owner()
    @developer_commands.command()
    async def activemail(self, ctx: commands.Context):
        """
        Previews how active mailsystem servers.
        """
        guild_list = []
        all_config = await self.config.all_guilds()
        for guild_id in all_config:
            if all_config[guild_id]["activation"]:
                guild_obj = ctx.bot.get_guild(guild_id)
                if not guild_obj:
                    try:
                        guild_obj = await ctx.bot.fetch_guild(guild_id)
                    except discord.HTTPException:
                        continue
                guild_list.append(guild_obj)

        msg = ""

        counter = 1
        for entry in guild_list:
            msg += f"[{counter}]:   {entry.name} - {entry.id}\n"

        message = "Active guilds: " + box(msg, lang="md")
        for page in pagify(message):
            await ctx.send(page)

    @checks.is_owner()
    @developer_commands.command(name="guildconfig")
    async def check_guild_config(self, ctx: commands.Context, guild: discord.Guild):
        """
        Checks config for given guild for help.

        Allows you to check the settings per guild to help verify everything is set properly.
        """
        guild_config = await self.config.guild(guild).all()
        embed = await EmbedSettings.embed_list_setting(self, ctx, guild_config, guild)

        await ctx.send(embed=embed)

    @checks.is_owner()
    @developer_commands.command(name="version")
    async def current_cog_version(self, ctx: commands.Context):
        """
        Displays current version.
        """
        await ctx.send("The current version is: `{version}`".format(version=self.__version__))

    @checks.is_owner()
    @developer_commands.command(hidden=True)
    async def blockguild(self, ctx: commands.Context, guild: discord.Guild):
        """
        Blocks guilds from setting up mailsystem.
        """
        ...
