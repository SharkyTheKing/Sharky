from typing import Optional

import discord
from redbot.core import checks, commands
from redbot.core.utils.chat_formatting import box, pagify

from .mixins import FilterSystemMixin


class StaffCommands(FilterSystemMixin):
    """
    Staff commands to handle settings
    """

    @commands.guild_only()
    @commands.group(pass_context=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def filter(self, ctx):
        """
        Filter System
        `Usage: [p]filter [add:remove] [strict:whitelist:exact] (channel is optional) words/sentences`

        Parameters:
            **Strict**: str, Will filter anything containing this phrase. (Non-Word Bound)
            **Exact**: str, Will filter anything that matches exactly phrase. (Word Bound)

        For more information on Strict/Exact [click here](https://gist.github.com/9a4a362cc84b2d036183c4d8d9cc2b7d) This needs to be updated
        """
        if ctx.invoked_subcommand is None:
            pass

    @filter.command(name="filterlog")
    async def channel_log(self, ctx, channel: Optional[discord.TextChannel]):
        """
        Sets logging channel for deleted words.

        Displays a log of all words that have been filtered.
        If no input is given, it'll clear the channel.
        """
        if channel is None:
            await self.config.guild(ctx.guild).filter_log.clear()
            return await ctx.send(
                "Cleared logging channel, will no longer log messages that have been filtered."
            )

        await self.config.guild(ctx.guild).filter_log.set(channel.id)
        return await ctx.send(
            "Will now log messages that have been filtered to {}.".format(channel.mention)
        )

    @filter.group(name="add")
    async def global_add(self, ctx):
        """
        Add a word/sentence to the guild filter.
        """
        pass

    @global_add.command(name="strict")
    async def guild_word_filter(self, ctx, channel: Optional[discord.TextChannel], *, word: str):
        """
        Adds a word/sentence to the guild filter.

        This specific filter will delete any messages containing the content listed. Words in this list are NOT surrounded by a word bound.

        Example:
            `"shark"` would remove `"sharky", "sharks", "sharkytheking"`
        """
        pass

    @global_add.command(name="exact")
    async def guild_exact_filter(self, ctx, channel: Optional[discord.TextChannel], *, word: str):
        """
        Adds a word/sentence to the guild exact filter.

        This specific filter will delete messages with an EXACT copy of the content listed. Words in this list ARE surrounded by a word bound.

        Example:
            `"shark"` would NOT remove `"sharky", "sharks", "sharkytheking"` but it WOULD remove `"shark is a king"`
        """
        pass


# TODO I need to completely redo the bottom part. Multiple issues arises from handling *where* each filter hit is from.
#    @filter.command(name="detect")
#    async def message_detection(self, ctx, channel: Optional[discord.TextChannel], word: str):
#        """
#        This will show you what words are being hit by filters.

#        Channel is optional
#        """
# This will be changed out to cache version once I get that in. This is purely used as test by test basis so I don't scram my head into a wall.
#        hit_list = []

#        all_global_config = await self.config.guild(ctx.guild).all()
#        filter_config = all_global_config["filter"]
#        exact_config = all_global_config["exact"]
#        whitelist_config = all_global_config["whitelist"]

#        if filter_config:
#            filter_regex = re.compile("|".join(rf"{re.escape(w)}" for w in filter_config))
#            if filter_regex is not None:
#                filter_hit = filter_regex.findall(word.lower())
#                hit_list.extend()

#        if exact_config:
#            exact_regex = re.compile("|".join(rf"\b{re.escape(w)}\b" for w in exact_config))
#            if exact_regex is not None:
#                exact_hit = exact_regex.findall(word.lower())
