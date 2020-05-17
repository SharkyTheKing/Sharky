from .verification import Verify


async def setup(bot):
    settings = Verify(bot)
    bot.add_cog(settings)
