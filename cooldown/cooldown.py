import discord
import asyncio
from redbot.core import commands, checks
from redbot.core.data_manager import bundled_data_path

class Cooldown(commands.Cog):
    """Testing Cooldowns out"""


#Follow the command line below to cooldown default per command
#For guide on BucketType types reference to https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.cooldown
    @commands.cooldown(1, 15, discord.ext.commands.BucketType.default)
    @commands.command()
    async def defaulttest(self, ctx):
        """Cooldown for default"""
        await ctx.send("This is a cooldown for default BucketType")

#Follow the command line below to cooldown a user per command
    @commands.cooldown(1, 15, discord.ext.commands.BucketType.user)
    @commands.command()
    async def usertest(self, ctx):
        """Cooldown for user"""
        await ctx.send("This is a cooldown per users BucketType")

#Follow the command line below to cooldown a guild as a whole, per command
    @commands.cooldown(1, 15, discord.ext.commands.BucketType.guild)
    @commands.command()
    async def guildtest(self, ctx):
        """Cooldown for guild"""
        await ctx.send("This is a cooldown per guild BucketType")

#Follow the command line below to cooldown a channel as a whole, per command
    @commands.cooldown(1, 15, discord.ext.commands.BucketType.channel)
    @commands.command()
    async def channeltest(self, ctx):
        """Cooldown for channel"""
        await ctx.send("This is a cooldown per channel BucketType")

#Follow the command line below to cooldown a member(of a guild) per command
    @commands.cooldown(1, 15, discord.ext.commands.BucketType.member)
    @commands.command()
    async def membertest(self, ctx):
        """Cooldown for member"""
        await ctx.send("This is a cooldown per member BucketType")

#Follow the command line below to cooldown a category per command
    @commands.cooldown(1, 15, discord.ext.commands.BucketType.category)
    @commands.command()
    async def categorytest(self, ctx):
        """Cooldown for category"""
        await ctx.send("This is a cooldown per category BucketType")
