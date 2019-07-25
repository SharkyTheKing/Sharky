from .charlimit import Charlimit
from redbot.core.bot import Red


async def setup(bot: Red):
    charlimit = Charlimit(bot)
    bot.add_cog(charlimit)
