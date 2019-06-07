from redbot.core.bot import Red
from .mute import Silence


def setup(bot: Red):
    bot.add_cog(Silence(bot))
