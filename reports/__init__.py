from .core import Reports


async def setup(bot):
    bot.add_cog(Reports(bot))
