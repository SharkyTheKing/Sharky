import discord
import datetime
import asyncio
from redbot.core import commands, checks
from redbot.core.data_manager import bundled_data_path

class Cooldown(Basecog):
    """Testing things out"""


#Import datetime as seen on line 2, follow the command line below to a command down for a user
    @commands.cooldown(1, 20, discord.ext.commands.BucketType.user)
    @commands.command()
    async def testing(self,ctx):
        """Cooldown placement"""
        await ctx.send("Nothing here. Curious what this is though? Learning how to make cooldowns per commands and how to set cooldowns. :D")