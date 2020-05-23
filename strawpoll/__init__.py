from .core import StrawPoll


def setup(bot):
    bot.add_cog(StrawPoll(bot))
