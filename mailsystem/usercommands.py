import asyncio

import discord
from redbot.core import commands

from .mail_logic import MailLogic
from .mixins import MailSystemMixin

# NOTE: For now, don't allow for on_message. I will need to code


class UserCommands(MailSystemMixin):
    """
    Commands related to users only.

    This is to clean up code on the main section.
    All of these are DMs only.
    """

    async def _create_new_ticket(self, ctx):
        """
        Internal function to create new ticket for user.
        """
        dict_guild = await MailLogic.get_mutual_guilds(self, ctx)

        if not dict_guild:
            await ctx.send("I'm sorry, there's no mutual servers that have modmail activated.")
            return False

        if len(dict_guild) == 1:
            await ctx.send(
                "Do you want to create a ticket for {}? Yes or No.".format(dict_guild[1])
            )
            confirm = await self._return_yes_or_no(ctx)

            if not confirm:
                await ctx.send("Canceled. Will not create the ticket.")
                return False

            check_guild_block = await self._return_guild_user_block(dict_guild[1], ctx.author.id)
            if check_guild_block:
                await ctx.send("Sorry, the guild has blocked you from making tickets.")
                return False

            channel = await MailLogic.create_channel_for_user(self, ctx, dict_guild[1], ctx.author)

            if not channel:
                await ctx.send(
                    "Error. Unable to create the channel. Please contact the staff team of the server."
                )
                return False

            await MailLogic._update_channel_info(self, ctx, ctx.author, channel)

        else:
            guild_choice = await MailLogic.get_guild_from_user(
                self=self, ctx=ctx, dict_guild=dict_guild
            )

            if not guild_choice:
                return False

            check_guild_block = await self._return_guild_user_block(guild_choice, ctx.author.id)
            if check_guild_block:
                await ctx.send("Sorry, the guild has blocked you from making tickets.")
                return False

            channel = await MailLogic.create_channel_for_user(self, ctx, guild_choice, ctx.author)

            if not channel:
                await ctx.send(
                    "Error. Unable to create the channel. Please contact the staff team of the server."
                )
                return False

            await MailLogic._update_channel_info(
                self=self, ctx=ctx, user=ctx.author, channel=channel
            )

        return channel

    @commands.command(usage="<Message To Mods>")
    @commands.dm_only()
    async def dmmail(self, ctx: commands.Context, *, contents: str):
        """
        Send mail to the staff of a server
        """
        confirm_global_block = await self._return_global_user_block(ctx.author.id)
        if confirm_global_block:
            return await ctx.send(
                "The bot owner has blocked you from accessing the mailsystem commands."
            )

        user_cache = MailLogic.check_tied_for_user(self, ctx.author.id)

        if not user_cache:
            new_ticket = await self._create_new_ticket(ctx=ctx)

            if not new_ticket:
                return  # await ctx.send(
                # "Error. Something went wrong when trying to make a new ticket."
                # )

            embed = self._return_embed_to_mod(ctx, contents)
            if not embed:
                # Need to change this around. Embed won't fail, but need to check for message or embeds
                ...

            record_log = await MailLogic._record_channel_creation(
                self, ctx, new_ticket, ctx.author
            )
            if not record_log:
                self.log.debug(
                    "Error. Was unable to log to {guild_name}'s logging channel.".format(
                        guild_name=new_ticket.guild
                    )
                )

            send = await self._send_channel_embed(new_ticket, embed)
            if not send:
                return await ctx.send(
                    "Error. Couldn't send ticket. Please contact the staff of the server."
                )

        elif user_cache:
            channel = await self._return_channel_object(ctx, user_cache)

            check_guild_block = await self._return_guild_user_block(channel.guild, ctx.author.id)
            if check_guild_block:
                await ctx.send("Sorry, the guild has blocked you from making tickets.")
                return False
                # This shouldn't happen, though on the off chance it does...handled.

            embed = self._return_embed_to_mod(ctx, contents)

            send = await self._send_channel_embed(channel, embed)
            if not send:
                return await ctx.send(
                    "Error. Couldn't send ticket. Please contact the staff of the server."
                )

        embed = self._return_mod_embed_for_user(embed)

        await self._send_user_embed(ctx.author, embed)

    @commands.command(usage="")
    @commands.dm_only()
    async def stopmail(self, ctx: commands.Context):
        """
        Closes your current mail ticket.
        """
        await ctx.send(
            "Currently this is not available.\n\n"
            "If you need your mail closed, please reach out to the staff of the server you have it tied to.\n\nIf the staff are unable to help, please contact the Owner of this bot.\n\n"
            "This is still planned, though due to repeated issues that cropped up, I (Sharky) have decided to hold this off and not prevent this from releasing the code."
        )
        # make sure to send something to the moderators
