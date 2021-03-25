import asyncio
import logging
from typing import Optional

import discord
from redbot.core import Config, checks, commands

DEF_GUILD = {
    "news_channels": [],
    "alert_channel": None,
    "notify_failed": False,
    "notify_success": False,
}

BASECOG = getattr(commands, "Cog", object)


class NewsPublish(BASECOG):
    """
    For Guilds that have News Channels!
    """

    __author__ = ["SharkyTheKing"]
    __version__ = "1.1.0"

    def __init__(self, bot):
        self.bot = bot
        self.log = logging.getLogger("red.cogs.newspublish")
        self.config = Config.get_conf(self, identifier=23462345, force_registration=True)
        self.config.register_guild(**DEF_GUILD)

    async def red_delete_data_for_user(self, **kwargs):
        """
        Nothing to delete
        """
        return

    def format_help_for_context(self, ctx: commands.Context) -> str:
        context = super().format_help_for_context(ctx)
        authors = ", ".join(self.__author__)
        return f"{context}\n\nAuthor: {authors}\nVersion: {self.__version__}"

    async def is_in_list(self, guild: discord.Guild, channel: discord.TextChannel):
        """
        Checks config for channel.

        Returns True if in config, returns False if not.
        """
        config_list = await self.config.guild(guild).news_channels()
        return True if channel.id in config_list else False

    @commands.group(name="publishset")
    @commands.guild_only()
    @checks.mod_or_permissions(manage_channels=True)
    async def publish_settings(self, ctx):
        """
        Adjust settings. Send nothing to preview settings

        Remember to set an alert channel for yourself, Discord ratelimits will prohibit publishing in a certain time frame.
        """
        pass

    @publish_settings.command(name="list")
    async def show_settings(self, ctx):
        """
        Displays settings for current guild.
        """
        guild_config = await self.config.guild(ctx.guild).all()
        alert_channel = guild_config["alert_channel"]
        news_channels = guild_config["news_channels"]
        failed_alerts = guild_config["notify_failed"]
        success_alerts = guild_config["notify_success"]

        list_of_channels = []
        if news_channels:
            for channel in news_channels:
                channel_obj = discord.utils.get(ctx.guild.channels, id=channel)

                if not channel_obj:
                    async with self.config.guild(ctx.guild).news_channels() as news_chan:
                        news_chan.remove(channel)
                    continue

                list_of_channels.append(channel_obj)

        if list_of_channels:
            channels = ", ".join(chan.mention for chan in list_of_channels)
        else:
            channels = "None set"
        embed = discord.Embed()
        embed.title = "{}'s Settings".format(ctx.guild.name)
        embed.add_field(
            name="Alert Channel",
            value="<#{}>".format(alert_channel) if alert_channel else "None",
        )
        embed.add_field(name="News Channel", value=channels, inline=False)
        embed.add_field(name="Alert Fails", value="Enabled" if failed_alerts else "Disabled")
        embed.add_field(name="Alert Success", value="Enabled" if success_alerts else "Disabled")
        await ctx.send(embed=embed)

    @publish_settings.command(name="addnews")
    async def set_news_channel(self, ctx, channel: discord.TextChannel):
        """
        Adds channel to publish list

        To remove, please use `[p]publishset removenews channel-name`
        """
        if not channel.is_news():
            return await ctx.send("{} is not a News Channel.".format(channel.mention))

        if channel.permissions_for(ctx.guild.me).manage_messages is False:
            return await ctx.send(
                "I do not have `manage_messages` in {} to publish. Please adjust my permissions.".format(
                    channel.mention
                )
            )

        if await self.is_in_list(guild=ctx.guild, channel=channel):
            return await ctx.send(
                "{} is already in the publish list. Nothing for me to add.".format(channel.mention)
            )

        async with self.config.guild(ctx.guild).news_channels() as news:
            news.append(channel.id)

        await ctx.send("Added {} to publish watchlist.".format(channel.mention))

    @publish_settings.group(name="alert")
    async def alert_settings(self, ctx):
        """
        Adjust alerts for fails and success publish.
        """
        pass

    @alert_settings.command(name="fail")
    async def enable_fail_alerts(self, ctx):
        """
        Enables / Disables alerts for fail publishes.
        """
        if await self.config.guild(ctx.guild).notify_failed() is False:
            await self.config.guild(ctx.guild).notify_failed.set(True)
            await ctx.send("Will now send alerts on failed publishes.")
        else:
            await self.config.guild(ctx.guild).notify_failed.set(False)
            await ctx.send("Will not send alerts on failed publishes.")

    @alert_settings.command(name="success")
    async def enable_success_alerts(self, ctx):
        """
        Enables / Disables alerts for success publishes.
        """
        if await self.config.guild(ctx.guild).notify_success() is False:
            await self.config.guild(ctx.guild).notify_success.set(True)
            await ctx.send("Will now send alerts on publish success.")
        else:
            await self.config.guild(ctx.guild).notify_success.set(False)
            await ctx.send("Will not send alerts on publish success.")

    @publish_settings.command(name="removenews")
    async def remove_news_channel(self, ctx, channel: discord.TextChannel):
        """
        Removes channel from publish list

        To add, please use `[p]publishset addnews channel-name`
        """
        if not await self.is_in_list(guild=ctx.guild, channel=channel):
            return await ctx.send(
                "{} is not in the publish list. Nothing for me to remove.".format(channel.mention)
            )

        async with self.config.guild(ctx.guild).news_channels() as news:
            news.remove(channel.id)

        await ctx.send("Removed {} from the publish watchlist.".format(channel.mention))

    @alert_settings.command(name="channel")
    async def alert_moderators_channel(self, ctx, channel: Optional[discord.TextChannel]):
        """
        Sends alert to the channel if bot failed to publish
        """
        if channel is None:
            await self.config.guild(ctx.guild).alert_channel.set(None)
            return await ctx.send("Done. Cleared the alert channel.")

        if (
            await self.config.guild(ctx.guild).notify_failed() is False
            and await self.config.guild(ctx.guild).notify_success() is False
        ):
            await ctx.send(
                "**Warning: This will not send anything if the publish fails / succeeds. Please enable either of these options.**"
            )

        await self.config.guild(ctx.guild).alert_channel.set(channel.id)
        await ctx.send("Done. Set alert channel to {}".format(channel.mention))

    @commands.Cog.listener()
    async def on_message_without_command(self, message):
        """
        Listens for news
        """
        channel, guild = message.channel, message.guild

        if not isinstance(message.guild, discord.Guild):
            return

        if await self.bot.cog_disabled_in_guild(self, message.guild):
            return

        if not await self.is_in_list(guild=guild, channel=channel):
            return

        try:
            await asyncio.wait_for(message.publish(), timeout=60)
            self.log.info("Published message in {} - {}".format(message.guild.id, channel.name))
            return await self.send_alert_message(message=message, alert_type="Success")
        except asyncio.TimeoutError:
            self.log.info(
                "Failed to publish message in {} - {}".format(message.guild.id, channel.name)
            )
            return await self.send_alert_message(message=message, alert_type="HTTPException")

    async def send_alert_message(self, message, alert_type):
        """
        Sends alert if it exists.
        Guild = message.guild
        """
        channel, guild = message.channel, message.guild
        guild_config = await self.config.guild(guild).all()
        alert_channel = guild_config["alert_channel"]
        failed_alerts = guild_config["notify_failed"]
        success_alerts = guild_config["notify_success"]

        embed = discord.Embed()

        if alert_channel is None:
            return  # Don't alert
        if alert_type == "HTTPException":
            if failed_alerts is False:  # Don't send alerts if this isn't enabled.
                return

            embed.title = "Failed Publish"
            embed.description = (
                "Can't publish [message in {}]({}). Hit 10 publish per user cap.".format(
                    channel.mention, message.jump_url
                )
            )

            try:
                return await self.bot.get_channel(alert_channel).send(embed=embed)
            except discord.Forbidden:
                self.log.info(
                    "Forbidden. Couldn't send message to {} - {} channel.".format(
                        guild.id, alert_channel
                    )
                )

        if alert_type == "Success":
            if success_alerts is False:  # Don't send alerts if this isn't enabled.
                return

            embed.title = "Success Publish"
            embed.description = "[Published new message in {}.]({})".format(
                channel.mention, message.jump_url
            )

            try:
                return await self.bot.get_channel(alert_channel).send(embed=embed)
            except discord.Forbiden:
                self.log.info(
                    "Forbidden. Couldn't send message to {} - {} channel.".format(
                        guild.id, alert_channel
                    )
                )
