from .core import NewsPublish


async def setup(bot):
    bot.add_cog(NewsPublish(bot))
