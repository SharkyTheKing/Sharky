from .lockdown import Lockdown


async def setup(bot):
    lockdown = Lockdown(bot)
    bot.add_cog(lockdown)
