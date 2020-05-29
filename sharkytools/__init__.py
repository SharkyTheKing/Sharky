from .core import SharkyTools


async def setup(bot):
    bot.add_cog(SharkyTools(bot))
