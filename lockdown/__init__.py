from .core import Lockdown


async def setup(bot):
    bot.add_cog(Lockdown(bot))
