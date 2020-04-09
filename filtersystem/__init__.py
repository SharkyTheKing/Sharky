from .filter import FilterSystem


def setup(bot):
    bot.add_cog(FilterSystem(bot))
