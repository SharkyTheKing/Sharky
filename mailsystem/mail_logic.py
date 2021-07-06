import asyncio
from typing import Optional

import discord
from redbot.core import commands
from redbot.core.utils.chat_formatting import box, pagify


class MailLogic:
    """
    The system logic for sending/creating mod mail/deleting mod mail.
    """

    def check_tied_for_user(self, user_id: int):
        """
        Checks tied channel to user
        """
        user_channel = {v: k for k, v in self.cache.items()}
        try:
            user_channel[user_id]
            return user_channel[user_id]
        except KeyError:
            return False
        return False

    def check_tied_for_channel(self, channel_id: int):
        """
        Checks tied user to channel
        """
        channel_user = self.cache
        try:
            channel_user[channel_id]
            return channel_user[channel_id]
        except KeyError:
            return False
        return False

    async def get_mutual_guilds(self, ctx: commands.Context):
        """
        Retrieves mutual guilds
        """
        shared_guild = [m.guild for m in ctx.bot.get_all_members() if m.id == ctx.author.id]

        list_guilds = {}
        counter = 1
        for guild in shared_guild:
            if await self.config.guild(guild).activation() is True:
                list_guilds.update({counter: guild})
                counter += 1

        if not list_guilds:
            return False

        return list_guilds

    async def get_guild_from_user(self, ctx: commands.Context, dict_guild):
        """
        Retrieves the guild from the user
        """
        dict_message = "".join(
            "[{counter}]: {guild_name}\n".format(counter=key, guild_name=val)
            for key, val in dict_guild.items()
        )

        choose_message = "Please choose a server:\n" + box(dict_message, lang="css")
        for page in pagify(choose_message):
            await ctx.send(page)

        confirm = await self._return_channel_or_no(ctx)

        if not confirm:
            return False

        try:
            chosen_guild = int(confirm.content)
        except ValueError:
            await ctx.send("Error. This is not a valid number.")
            return False

        try:
            dict_guild[chosen_guild]
        except KeyError:
            await ctx.send("This is not a given option.")
            return False

        return dict_guild[chosen_guild]

    async def delete_channel_for_user(self, channel: discord.TextChannel):
        """
        Deletes the channel tied to the user.
        """
        try:
            await channel.delete(reason="Mail Channel closed.")
        except (discord.Forbidden, discord.NotFound, discord.HTTPException):
            return False
        return True

    async def _remove_channel_info(self, channel):
        """
        Internal function to remove info from channel and cache
        """
        await self.config.channel(channel).clear()
        try:
            self.cache.pop(channel.id)
        except KeyError:
            return False
        return True

    async def _record_channel_deletion(
        self, ctx: commands.Context, reason: Optional[str], user_id: Optional[int]
    ):
        """
        Internal function to handle channel deletion logging.
        """
        embed = discord.Embed(title="Mail Closed.")
        embed.set_author(name="{mod} - {mod_id}".format(mod=ctx.author, mod_id=ctx.author.id))
        embed.set_thumbnail(url=ctx.author.avatar_url)

        if reason:
            embed.description = "**Reason:** " + reason
        else:
            embed.description = "No reason was provided."

        if user_id:
            member = ctx.guild.get_member(user_id)
            if member:
                embed.set_footer(
                    text="{member} | {member_id}".format(member=member, member_id=member.id)
                )
                embed.timestamp = ctx.message.created_at

        send_log = await MailLogic._send_to_log(
            self=self, guild=ctx.guild, content=None, embed=embed
        )
        return bool(send_log)

    async def create_channel_for_user(self, ctx: commands.Context, guild: discord.Guild, user):
        """
        Creates channel tied to user

        --------
        cache update channel.id: user
        """
        category_config = await self.config.guild(guild).category()
        category = ctx.bot.get_channel(category_config)
        if not category:
            try:
                category = await ctx.bot.fetch_channel(category_config)
            except discord.HTTPException as error:
                self.log.debug(f"Unable to get category channel in {guild.id} - {error.status}")
                return False

        try:
            channel = await category.create_text_channel(name=user.id)
        except discord.Forbidden:
            self.log.debug(f"Forbidden to create channel in {guild.id}")
            return False
        except discord.HTTPException as error:
            self.log.debug(f"Failed to create channel in {guild.id} - {error.status}")
            return False

        return channel  # Allow for return, so we can handle in case it fails on creating channel.

    async def _update_channel_info(self, ctx: commands.Context, user, channel):
        """
        Internal function to update config and cache
        """
        await self.config.channel(channel).user.set(ctx.author.id)
        self.cache.update({channel.id: ctx.author.id})

    async def _record_channel_creation(
        self, ctx: commands.Context, channel: discord.TextChannel, user
    ):
        """
        Inteneral function on logging channel creations
        """
        embed = discord.Embed(title="Mail Opened.")
        embed.set_author(name="{user} - {user_id}".format(user=user.name, user_id=user.id))
        embed.description = "New Mail Ticket created."
        embed.set_thumbnail(url=user.avatar_url)

        embed.timestamp = ctx.message.created_at

        send_log = await MailLogic._send_to_log(
            self=self, guild=channel.guild, content=None, embed=embed
        )
        return bool(send_log)

    async def _send_to_log(
        self, guild: discord.Guild, content: Optional[str], embed: Optional[discord.Embed]
    ):
        """
        Internal function to send contents and/or messages to log channel.

        If content is none, send embed, else send content.
        """
        channel_config = await self.config.guild(guild).mail_log_channel()
        if not channel_config:
            return True  # Odd yes, though needed to prevent debug log

        log_channel = guild.get_channel(channel_config)
        if not log_channel:
            try:
                log_channel = await guild.fetch_channel(channel_config)
            except discord.HTTPException as error:
                self.log.debug(f"HTTPException in {guild.id} - {error.status}")
                return False

        try:
            await log_channel.send(content=content, embed=embed)
        except discord.HTTPException as error:
            self.log.debug(f"Failed to send to log channel. {guild.id} - {error.status}")
            return False
        return True
