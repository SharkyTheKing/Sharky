import discord
import time
import asyncio
from redbot.core import commands, check
from redbot.core.data_manager import bundled_data_path

class Cooldown(commands.cog):
    """Testing things out"""


#Command placement
    @commands.group()
    async def cooldown(self,ctx):
        """Cooldown placement"""
        await ctx.send("Nothing here. Curious what this is though? Learning how to make cooldowns per commands and how to set cooldowns. :D")