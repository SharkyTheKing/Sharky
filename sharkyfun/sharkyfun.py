import discord
import asyncio
from redbot.core import commands, checks
from redbot.core.data_manager import bundled_data_path

class SharkyFun(commands.Cog):
    """A personal fun cog full of Shark/Fishy related humor"""
    @commands.cooldown(1, 15, discord.ext.commands.BucketType.user)
    @commands.command()
    async def banhammer(self, ctx):
        """Swing that hammer"""
        file = discord.File(str(bundled_data_path(self) / "catban.png"))
        async with ctx.typing():
            await ctx.send(files=[file])