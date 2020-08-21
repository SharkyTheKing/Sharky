from .core import NameGen


def setup(bot):
    bot.add_cog(NameGen(bot))