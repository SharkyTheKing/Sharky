from .linky import AntiLinks
from redbot.core.bot import Red


async def setup(bot: Red):
    antilinks = AntiLinks(bot)
    bot.add_cog(antilinks)