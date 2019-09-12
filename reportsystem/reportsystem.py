import discord
from typing import Optional
from redbot.core import Config, checks, commands
from typing import Union

BaseCog = getattr(commands, "Cog", object)


class ReportSystem(BaseCog):
    """
    Report System

    Members can type `[p]report <user> <reason>` and it'll show up in your selected channel!
    """

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=923485973)
        def_guilds = {"report": None, "emote": False}
        self.config.register_guild(**def_guilds)

    #   Report command
    @commands.guild_only()
    @commands.cooldown(2, 15, commands.BucketType.user)
    @commands.command()
    async def report(self, ctx, member: Optional[discord.Member], *, reason: str):
        """
        Report a member to the moderation team!
        """
        bot = ctx.bot
        guild = ctx.guild
        color = await ctx.embed_color()
        log = await self.config.guild(guild).report()
        mem = ""
        if member is None:
            mem = "No users detected"
        else:
            if member.nick is not None:
                mem += f"{member.mention}\n**Nick**: {member.nick}\n**ID**: {member.id}"
            else:
                mem += f"{member.mention}\n**ID**: {member.id}"
        try:
            await ctx.message.delete()
        except (discord.HTTPException, discord.Forbidden):
            pass
        embed = discord.Embed(color=color)
        embed.description = f"**Reason**:\n{reason}"
        embed.timestamp = ctx.message.created_at
        embed.add_field(name="User", value=mem)
        if member is None or member.voice is None:
            embed.add_field(name="Channel", value=f"{ctx.channel.mention}")
        else:
            embed.add_field(
                name="Channel",
                value=f"{ctx.channel.mention}\n**VC**: {member.voice.channel.mention}",
            )
        embed.add_field(name="Author", value=f"{ctx.author.mention}")
        if member is not None:
            member_avatar = member.avatar_url_as(static_format="png")
            embed.set_thumbnail(url=member_avatar)
        else:
            pass
        try:
            if log is None:
                await ctx.author.send(
                    "Sorry, but it appears no one has setup a report channel. Please notify the moderators of the server!"
                )
            else:
                await bot.get_channel(log).send(embed=embed)
                await ctx.author.send(
                    "Thank you for your report. The moderation team has received your report."
                )
        except (discord.HTTPException, discord.Forbidden):
            pass

    @commands.command()
    @checks.mod()
    async def check(self, ctx, member: discord.Member):
        """
        Sends a message to the user that you have verified/checked the report

        A unique way of sending a message back to the members to let them know, you checked the reports
        """
        embed = discord.Embed(color=await ctx.embed_color())
        embed.title = "Report checked!"
        embed.timestamp = ctx.message.created_at
        embed.set_thumbnail(
            url="https://media.discordapp.net/attachments/575846797709279262/616887240101986344/OS-Fundraising-ChocolateChipTop_whitespace.png"
        )
        embed.description = "Your report has been checked by a moderator! Thank you for sending it in. Have a cookie! \N{COOKIE}"
        try:
            await member.send(embed=embed)
        except discord.Forbidden:
            pass

    @commands.group()
    @checks.admin()
    async def reportset(self, ctx):
        """Manage reports"""
        pass

    @reportset.command()
    @checks.admin_or_permissions(manage_guild=True)
    async def channel(self, ctx, channel: Optional[discord.TextChannel]):
        """Set a channel to be the channel reports get posted into"""
        if channel is not None:
            await self.config.guild(ctx.guild).report.set(channel.id)
            await ctx.send(f"Made {channel.mention} the reporting channel.")
        else:
            await self.config.guild(ctx.guild).report.set(None)
            await ctx.send(f"Disabled the report command and removed the reporting channel.")

    @reportset.command()
    @checks.admin_or_permissions(manage_guild=True)
    async def emote(self, ctx, toggle: Optional[bool]):
        """
        Sets it whether the bot automatically puts reactions for each report sent

        Up is confirming it's a valid report
        Down is confirming it's not a valid report
        Question means you're unsure of the report or are in question of it
        X means it's been too long to look into
        """
        emote = self.config.guild(ctx.guild).emote
        if toggle is None:
            await ctx.send("The current settings is set to {}".format(await emote()))
        elif toggle is True:
            await emote.set(True)
            await ctx.send("The setting is now set to {}".format(await emote()))
        elif toggle is False:
            await emote.set(False)
            await ctx.send("The setting is now set to {}".format(await emote()))

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user):
        report = await self.config.guild(reaction.message.guild).report()
        chan = ""
        if report is None:
            pass
        else:
            chan = discord.utils.get(reaction.message.guild.channels, id=int(report))
        if reaction.message.channel != chan:
            return False
        elif reaction.message.channel == chan:
            if user is reaction.message.author:
                return False
            else:
                try:
                    react = reaction.message
                    await react.edit(content="{} has claimed this.".format(user.display_name))
                except discord.Forbidden:
                    pass

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        Auto-add reactions
        """
        author = message.author
        report = await self.config.guild(message.guild).report()
        emote = self.config.guild(message.guild).emote
        if report is None:
            return False
        else:
            if await emote() is True:
                if author == self.bot.user:
                    chan = discord.utils.get(message.guild.channels, id=int(report))
                    if message.channel == chan:
                        react = ["👋", "👍", "👎", "❓", "❌"]
                        for emotes in react:
                            await message.add_reaction(emotes)
                    else:
                        pass
                else:
                    pass
            else:
                pass
