from redbot.core.bot import Red

from .charlimit import Charlimit

__red_end_user_data_statement__ = (
    "This cog does not persistently store data or metadata about users."
)


async def setup(bot: Red):
    charlimit = Charlimit(bot)
    bot.add_cog(charlimit)
