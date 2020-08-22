import typing
from typing import Optional

import discord
from redbot.core import checks, commands

BaseCog = getattr(commands, "Cog", object)


class Announcements(BaseCog):
    """
    A nice way of announcing a message in a certain channel while pinging a role
    """

    def __init__(self, bot):
        self.bot = bot

    async def red_delete_data_for_user(self, **kwargs):
        """
        Nothing to delete
        """
        return

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(manage_roles=True, send_messages=True)
    @checks.mod_or_permissions(manage_roles=True)
    async def alert(
        self,
        ctx,
        role: Optional[discord.Role],
        channel: Optional[discord.TextChannel],
        *,
        message: str,
    ):
        """
        Announce a message in a selected channel, while mentioning a role.

        Both role and channel are optional
        """
        await self._build_message(ctx, role, channel, message)

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(manage_roles=True, send_messages=True)
    @checks.mod_or_permissions(manage_roles=True)
    async def messageedit(self, ctx, message_id: int, message: str):
        """
        Edit a message by the bot!

        Please note that you can't edit a message that ISN'T from the bot
        """
        await self._build_edit(ctx, message_id, message)

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(manage_roles=True, send_messages=True)
    @checks.mod_or_permissions(manage_roles=True)
    async def mentionable(self, ctx, role: discord.Role):
        """
        Makes a role mentionable or unmentionable

        If a role is currently mentionable, use this command and it'll make unmentionable, as well as doing the opposite will work
        """
        await self._build_mentions(ctx, role)

    #   Building Announce message
    async def _build_message(
        self,
        ctx,
        role: typing.Tuple[discord.Role, None],
        channel: typing.Tuple[discord.TextChannel, None],
        message: str,
    ):
        """
        Internal message building function
        """
        if role is not None:
            await role.edit(mentionable=True)
            if channel is not None:
                await channel.send(f"{message}\n{role.mention}")
            else:
                await ctx.send(f"{message}\n{role.mention}")
            await role.edit(mentionable=False)
        else:
            if channel is not None:
                await channel.send(f"{message}")
            else:
                await ctx.send(f"{message}")

    #   Building Mentionable stuff
    async def _build_mentions(self, ctx, role: discord.Role):
        """
        Internal mentions
        """
        if role.mentionable is True:
            await role.edit(mentionable=False)
            await ctx.send(
                "Role is now not mentionable!\nTo make the role mentionable, please use `[p]mentionable role`"
            )
        elif role.mentionable is False:
            await role.edit(mentionable=True)
            await ctx.send(
                "Role is now mentionable!\nTo make the role **NOT** mentionable, please use `[p]unmentionable role`"
            )

    #   Building message edit
    async def _build_edit(self, ctx, message_id: int, message: str):
        """
        Internal edit
        """
        try:
            info = await ctx.fetch_message(message_id)
            await info.edit(content=message)
        except discord.Forbidden:
            await ctx.send("Can't edit a message that isn't from the bot.")
        except:
            await ctx.send("Something happened here that I can't explain, please reach out to me.")
