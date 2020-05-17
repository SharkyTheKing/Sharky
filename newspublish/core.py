import discord
from redbot.core import commands, Config, checks
from typing import Optional
import asyncio
import logging

DEF_GUILD = {"news_channels": [], "alert_channel": None}

BASECOG = getattr(commands, "Cog", object)


class NewsPublish(BASECOG):
    """
    For Guilds that have News Channels
    """

    def __init__(self, bot):
        self.bot = bot
        self.log = logging.getLogger("red.cogs.newspublish")
        self.config = Config.get_conf(self, identifier=23462345, force_registration=True)
        self.config.register_guild(**DEF_GUILD)

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
        if ctx.invoked_subcommand is None:
            alert_channel = await self.config.guild(ctx.guild).alert_channel()
            news_channels = await self.config.guild(ctx.guild).news_channels()
            channels = ""
            if news_channels:
                for channel in news_channels:
                    channels += "<#{}> - {}\n".format(channel, channel)
            else:
                channels = "None set"
            embed = discord.Embed()
            embed.title = "{}'s Settings".format(ctx.guild.name)
            embed.add_field(
                name="Alert Channel",
                value="<#{}>".format(alert_channel) if alert_channel else "None",
            )
            embed.add_field(name="News Channel", value=channels)
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

    @publish_settings.command(name="alertchannel")
    async def alert_moderators_channel(self, ctx, channel: Optional[discord.TextChannel]):
        """
        Sends an alert to this channel if bot failed to publish
        """
        if channel is None:
            await self.config.guild(ctx.guild).alert_channel.set(None)
            return await ctx.send("Done. Cleared the alert channel.")

        await self.config.guild(ctx.guild).alert_channel.set(channel.id)
        await ctx.send("Done. Set alert channel to {}".format(channel.mention))

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        Listens for news
        """
        #   Variables
        channel, guild = message.channel, message.guild

        if isinstance(message.guild, discord.Guild):
            if guild is None:
                return

        if not await self.is_in_list(guild=guild, channel=channel):
            return

        try:
            await asyncio.wait_for(message.publish(), timeout=60)
            self.log.info("Published message in {}".format(channel.name))
        except asyncio.TimeoutError:
            self.log.info("Couldn't publish within a minute..forwarding to alert channel")
            return await self.send_alert(message=message, error_type="HTTPException")

    async def send_alert(self, message, error_type):
        """
        Sends alert if it exists.
        Guild = message.guild
        """
        channel, guild = message.channel, message.guild
        alert_channel = await self.config.guild(guild).alert_channel()
        if alert_channel is None:
            return  # Don't alert
        if error_type == "HTTPException":
            try:
                return await self.bot.get_channel(alert_channel).send(
                    "Can't publish message in {}. Hit 10 publish per user cap.\nLink: {}".format(
                        channel.mention, message.jump_url
                    )
                )
            except discord.Forbidden:
                self.log.info("Forbidden. Couldn't send message to alert channel.")
