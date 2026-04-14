from .core import Counter


async def setup(bot):
    await bot.add_cog(Counter(bot))
