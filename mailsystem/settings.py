import asyncio
from typing import Optional

import discord
from redbot.core import checks, commands
from redbot.core.utils.chat_formatting import humanize_list

from .embedmodel import EmbedSettings


class MailSettings:
    """
    Staff commands that adjust MailSystem settings
    """

    @checks.admin_or_permissions(manage_guild=True)
    @commands.group(name="mailset")
    async def mailsystem_settings(self, ctx: commands.Context):
        """
        Sets the settings for mail system
        """
        ...

    @mailsystem_settings.command(name="commands", usage="<True/False>")
    @checks.is_owner()
    async def allow_commands_or_message(self, ctx: commands.Context, toggle: bool):
        """
        To use commands or on_message in DMs to trigger a new mail

        True sets it to commands only
        False sets it to use on_message event in Dms
        """
        return await ctx.send(
            "Currently this is unavailable. If you have suggestions or would like to help finish this, please reach out to the cog owner(s)."
        )

        if toggle is True:
            await self.config.enable_commands.set(True)
            return await ctx.send("Users MUST use a command for a new mail ticket.")
        elif toggle is False:
            await self.config.enable_commands.set(False)
            return await ctx.send("Users MUST send a regular DM to the bot for a new mail ticket.")

    @mailsystem_settings.command(name="logchannel", aliases=["log", "logging"])
    async def set_log_channel(self, ctx: commands.Context, channel: Optional[discord.TextChannel]):
        """
        Sets the channel to log channel deletions/creations

        If nothing is inputted, it'll clear the results.
        """
        if not channel:
            await self.config.guild(ctx.guild).mail_log_channel.set(None)
            return await ctx.send("Will no longer log channel deletions/creations.")

        #  May not make it require same category, we'll see.
        if channel.category.id != await self.config.guild(ctx.guild).category():
            return await ctx.send("You must put the logging channel in the MailSystem Category.")

        await self.config.guild(ctx.guild).mail_log_channel.set(channel.id)
        await ctx.send("Will now log channel deletions/creations to {}".format(channel.mention))

    @mailsystem_settings.command("embeds", usage="<True/False>")
    async def set_content_or_embed(self, ctx, toggle: bool):
        """
        Sets whether to use embeds or regular message
        """
        return await ctx.send(
            "Currently this is unavailable. If you have suggestions or would like to help finish this, please reach out to the cog owner(s)."
        )

        if toggle is True:
            await self.config.guild(ctx.guild).enable_embeds.set(True)
            return await ctx.send("New Modmails will now use embeds.")

        elif toggle is False:
            await self.config.guild(ctx.guild).enable_embeds.set(False)
            return await ctx.send("New Modmails will now use regular messages.\nt")

    @mailsystem_settings.command(name="category")
    async def set_mail_category(
        self, ctx: commands.Context, category: Optional[discord.CategoryChannel]
    ):
        """
        Sets the category to create mail channels in.

        If category isn't given, it'll clear the setting.
        """
        if not category:
            await self.config.guild(ctx.guild).category.clear()
            return await ctx.send("No category was provided, so the setting has been cleared.")

        if not (
            category.permissions_for(ctx.guild.me).manage_channels
            or ctx.guild.me.guild_permissions.administrator
        ):
            return await ctx.send(
                "I do not have `manage_channels` permissions. Please grant my role permission to manage channels or otherwise I cannot complete my task."
            )

        await self.config.guild(ctx.guild).category.set(category.id)
        await ctx.send("Done. Category is now set to {} ({})".format(category.name, category.id))

    @mailsystem_settings.command(name="activate", usage="<true/false>")
    async def activate_mail_system(self, ctx: commands.Context, toggle: bool):
        """
        Sets the system to be enabled or disabled
        """
        if not await self.config.guild(ctx.guild).category():
            return await ctx.send(
                "There is no category set yet. I cannot be enabled until a category is setup."
            )

        word = "enabled" if toggle else "disabled"
        await ctx.send("The system is now {}.".format(word))
        await self.config.guild(ctx.guild).activation.set(toggle)

    @mailsystem_settings.command(name="showsettings", aliases=["list", "settings"])
    async def show_mail_list(self, ctx: commands.Context):
        """
        Displays MailSystem settings
        """
        config_info = await self.config.guild(ctx.guild).all()
        embed = await EmbedSettings.embed_list_setting(self, ctx, config_info)

        await ctx.send(embed=embed)

    @checks.is_owner()
    @mailsystem_settings.command(name="warn")
    async def warn_message_for_owner(self, ctx: commands.Context):
        """
        Displays this cog's current warn message.
        """
        warn_message = "**Warning: This Cog is still in testing, by installing and USING this Cog, you understand it comes with risks.**\n\nThis pre-release is to gather information, feedback, and issues from the community to improve the code. If you feel uncomfortable using this cog in its current state, uninstall it now.\n\nIf you have feedback or have an issue (bugs, breakage, bot blocking, etc) please send them to the proper place."
        embed = discord.Embed(
            title="MailSystem Warning", color=discord.Color.random(), description=warn_message
        )
        embed.add_field(name="Current version:", value=self.__version__)
        embed.add_field(name="Authors:", value=humanize_list(self.__author__))
        embed.add_field(
            name="Repo:", value="[Sharky's Cogs](https://github.com/SharkyTheKing/Sharky)"
        )
        await ctx.send(embed=embed)


# TODO Once things are in proper terms, I will work on autosetup.
