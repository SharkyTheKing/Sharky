import discord
import datetime
import asyncio
from redbot.core import commands, checks
from redbot.core.data_manager import bundled_data_path

class Cooldown(commands.Cog):
    """Testing things out"""


#Import datetime as seen on line 2, follow the command line below to cooldown default per command
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
        """Cool down for guild"""
        await ctx.send("This is a cooldown per guild BucketType")

    
