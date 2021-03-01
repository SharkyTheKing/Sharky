import asyncio

import discord
from redbot.core import checks, commands
from redbot.core.utils.chat_formatting import box, pagify


class MessageTrackerDev:
    """
    Dev commands for Message Tracker.

    Do not use unless you understand the use cases.
    """

    @checks.is_owner()
    @commands.group(name="msgtrackdev")
    async def message_dev_tracker(self, ctx):
        """
        Owner Only: Dev commands for Message Tracker.

        Do not use unless you are aware of the commands involved
        """
        ...

    @checks.is_owner()
    @message_dev_tracker.command(name="nukeconfig")
    async def nuke_message_config(self, ctx):
        """
        Nukes all recorded counters.

        This will nuke every messages that's been counted. Do so at your own risk.
        """

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        await ctx.send(
            "Are you sure you want to nuke all member's config? This will reset counters for everyone on every server. (Yes/No)"
        )

        try:
            confirm_action = await ctx.bot.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            await ctx.send("You took too long to reply...")
            return False

        if confirm_action.content.lower() != "yes":
            await ctx.send("Okay. Won't nuke config.")
            return

        await self.config.clear_all_members()
        await ctx.send("Done. Config has been nuked.")

    @checks.is_owner()
    @message_dev_tracker.command(name="cache")
    async def messagetrackcache(self, ctx):
        """
        Check cached messages counter for this server.
        """
        if not self.counted_message:
            return await ctx.send("No messages tracked.")

        list_words = []

        try:
            sorting_list = sorted(
                self.counted_message[ctx.guild.id].items(),
                key=lambda x: x[1]["message"],
                reverse=True,
            )
        except KeyError:
            return await ctx.send(
                "Sorry, there's currently no messages being tracked for this server."
            )

        for userid, counter in sorting_list:
            list_words.append("{} {} messages".format(userid, counter["message"]))

        if not list_words:
            return False

        message_to_user = "Leaderboard:"

        for msg in list_words:
            message_to_user += "\n\t- {}".format(msg)

        for page in pagify(message_to_user):
            await ctx.send(box(page))

    @checks.is_owner()
    @message_dev_tracker.command(name="updateconfig")
    async def updatemessageconfig(self, ctx):
        """
        Updates to config manually
        """
        if not self.counted_message:
            return await ctx.send("Nothing to update")
        await self.update_config_from_cache()
        await ctx.send("Done. Config updated and cache reset.")
