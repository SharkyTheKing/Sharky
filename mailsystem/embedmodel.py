from typing import Optional

import discord
from redbot.core import commands


class EmbedModels:
    """
    Embed models for all things that gets sent
    """

    @staticmethod
    def embed_to_moderators(self, ctx: commands.Context, contents: str):
        """
        Embed that get's sent to staff

        This is not the embed that the user is shown.
        """
        embed = discord.Embed(description=contents, color=self.received_mail)

        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)

        embed.set_footer(text="User ID: {author_id}".format(author_id=ctx.author.id))

        return embed

    @staticmethod
    def mod_embed_for_user(self, embed):
        """
        Embed that shows to user what they sent to staff

        This is shown to the user to make sure they know their message got sent
        """
        embed.color = self.sent_mail
        embed.title = "Message Sent"

        return embed

    @staticmethod
    def embed_to_user(self, ctx: commands.Context, contents: str, anonymous: bool):
        """
        Embed that get's sent to the user

        -----
        bool: True - Hides staff's name/icon and shows guild's name/icon.
        bool: False - Displays staff name and icon.
        """
        embed = discord.Embed(description=contents, title="{} replied".format(ctx.guild.name))
        embed.color = self.received_mail
        embed.timestamp = ctx.message.created_at

        if anonymous:
            embed.set_author(name="Anonymous Reply", icon_url=ctx.guild.icon_url)
        elif not anonymous:
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)

        return embed

    @staticmethod
    def user_embed_for_mods(self, ctx: commands.Context, embed, anonymous: bool):
        """
        Embed that shows staff what is sent to user.

        Regardless of anonymous bool is set, it'll highlight what staff replied.

        -----
        bool: True - Says anonymous reply but shows staff's name/icon.
        bool: False - Displays staff name and icon.
        """
        embed.color = self.sent_mail
        if anonymous:
            embed.title = "Anonymous Message Sent"
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        elif not anonymous:
            embed.title = "Message Sent"

        return embed


class EmbedSettings:
    """
    Embed models for mailsystem's settings
    """

    async def embed_list_setting(self, ctx: commands.Context, config_info):
        """
        Display config settings to embed
        """
        embed = discord.Embed(
            title="{guild_name}'s Mail Settings".format(guild_name=ctx.guild.name),
            color=await ctx.embed_colour(),
        )

        embed.add_field(
            name="Category Name",
            value=discord.utils.get(ctx.guild.channels, id=config_info["category"])
            if config_info["category"]
            else "No category set",
            inline=False,
        )

        embed.add_field(
            name="Embeds or Messages",
            value="Embeds" if config_info["enable_embeds"] else "Messages",
        )

        embed.add_field(
            name="Enabed/Disabled",
            value="Enabled" if config_info["activation"] else "Disabled",
            inline=False,
        )

        global_toggle = await self.config.enable_commands()

        embed.add_field(
            name="Commands/Messages",
            value="Must use a command in Bot's DM."
            if global_toggle
            else "Must send a direct message to the Bot.",
        )

        embed.add_field(
            name="Logging Channel",
            value=self.bot.get_channel(config_info["mail_log_channel"]).mention
            if config_info["mail_log_channel"]
            else "No logging category set",
            inline=False,
        )

        return embed
