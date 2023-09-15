from .core import MsgTracker


async def setup(bot):
    cog = MsgTracker(bot)
    await bot.add_cog(cog)
