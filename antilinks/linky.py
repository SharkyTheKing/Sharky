import discord
import re
from redbot.core import commands, Config, checks
from redbot.core.bot import Red
import url_regex


BaseCog = getattr(commands, "Cog", object)


class AntiLinks(BaseCog):
    """Prohibit links from being sent unless allowed."""

    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=12351232352234)

        def_channel = {"whitelist": [], "active": False}
        def_guild = {"logs": None}
        self.config.register_channel(**def_channel)
        self.config.register_guild(**def_guild)

    @commands.guild_only()
    @commands.group()
    @checks.mod_or_permissions(manage_channels=True)
    async def linkset(self, ctx):
        """
        Manage the AntiLink settings
        """
        pass

    @linkset.command()
    async def whitelist(self, ctx, channel: discord.TextChannel, *, urls: str):
        """
        Whitelist the links for the channel you set
        """
        link = ""
        find_link = url_regex.UrlRegex(urls, strict=False)
        c_conf = self.config.channel(channel)
        if find_link.detect:  # Detect returns a True or False
            link = find_link.links[0].domain  # full = Full link | domain = Only domain part
            async with c_conf.whitelist() as white:
                if link not in white:
                    white.append(link)
                    await ctx.send("The link has been whitelisted for {}".format(channel.mention))
                elif link in white:
                    return await ctx.send("That links is already whitelisted there.")
        elif find_link.detect is False:
            await ctx.send("Couldn't find a link in your message.")

    @linkset.command()
    async def remove(self, ctx, channel: discord.TextChannel, *, urls: str):
        """
        Removes a link from the whitelist of whichever channel you select
        """
        link = ""
        find_link = url_regex.UrlRegex(urls, strict=False)
        c_conf = self.config.channel(channel)
        if find_link.detect is True:
            link = find_link.links[0].domain
            async with c_conf.whitelist() as white:
                if link in white:
                    white.remove(link)
                    await ctx.send("The link has been removed for {}".format(channel.mention))
                elif link not in white:
                    return await ctx.send("That link is not there.")
        elif find_link.detect is False:
            await ctx.send("Couldn't find a link in your message.")

    @linkset.command()
    async def log(self, ctx, channel: discord.TextChannel = None):
        """
        Sets the channel to log link deletions
        """
        guild = ctx.guild
        if channel is None:
            await self.config.guild(guild).logs.set(None)
            await ctx.send("Will not log any deleted messages")
        else:
            await self.config.guild(guild).logs.set(channel.id)
            await ctx.send("Set the logging channel to {}".format(channel.mention))
            await channel.send("This will now be used for link logging")

    @linkset.command()
    async def active(self, ctx, channel: discord.TextChannel, toggle: bool):
        """
        Activates/Deactivates a channel being watched for links

        Default is False, to change use `[p]linkset active #channel True`
        """
        if toggle is False:
            await self.config.channel(channel).active.set(False)
            await ctx.send(f"{channel.mention} will not be watched anymore")
        elif toggle is True:
            await self.config.channel(channel).active.set(True)
            await ctx.send(f"{channel.mention} will be watched for links")

    @linkset.command()
    async def list(self, ctx, channel: discord.TextChannel = None):
        """
        Displays the channels used

        If a specific channel is mentioned, it'll show the links for that channel
        """
        color = await ctx.embed_color()
        if channel is None:
            guild = ctx.guild
            logs = await self.config.guild(guild).logs()
            info = ""
            for x in guild.channels:
                active = await self.config.channel(x).active()
                if active is True:
                    info += f"{x.mention}\n"
                elif active is False:
                    pass
            embed = discord.Embed(color=color)
            embed.title = f"{guild.name} settings"
            embed.add_field(name="Channels watched:", value=info if info else "None")
            embed.add_field(
                name="Logging Channel:", value=f"<#{logs}>" if logs else "No logging channel set"
            )
            await ctx.send(embed=embed)
        else:
            guild = ctx.guild
            links = ""
            link_info = self.config.channel(channel).whitelist
            for x in await link_info():
                links += f"{x}\n"
            active = self.config.channel(channel).active
            embed = discord.Embed(color=color)
            embed.title = f"{channel.name}'s settings"
            embed.add_field(name="Status:", value=await active())
            embed.add_field(name="Links:", value=links if links else "No links added")
            await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        current = message.channel
        author = message.author
        c_conf = await self.config.channel(current).whitelist()
        logs = await self.config.guild(message.guild).logs()
        check = await self.config.channel(current).active()

        if check is False:
            return False
        elif check is True:
            link_check = url_regex.UrlRegex(message.content, strict=False)
            embed = discord.Embed(color=message.guild.me.top_role.color)
            embed.title = f"{author.name}#{author.discriminator} - Link Deleted"
            embed.description = message.content
            embed.set_footer(text=f"User ID: {author.id}")
            if link_check.detect is True:
                content_info = link_check.links[0].full
                if content_info not in c_conf:
                    if (
                        current.permissions_for(message.author).manage_messages is True
                        or message.author.bot is True or await self.bot.is_automod_immune(author) is True
                    ):
                        return
                    try:
                        await message.delete()
                        if logs is None:
                            pass
                        else:
                            await self.bot.get_channel(logs).send(embed=embed)
                    except discord.Forbidden:
                        pass
                    except AttributeError:
                        pass
                else:
                    pass
            else:
                pass


# btw, it's set on strict mode by default
# strict mode means it will find links like "twitter.com" that doesn't have "www." nor "https://", to turn that off, do UrlRegex("text here", strict=False)
# btw if you want to get all links in a list (assuming you would push multiple) do
# [g.full for g in find_link.links]
# That will ensure that you have a list only with full links
