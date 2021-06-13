from .core import MsgTracker


async def setup(bot):
    cog = MsgTracker(bot)
    bot.add_cog(cog)
