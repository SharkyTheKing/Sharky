from .modmail import MailSystem


async def setup(bot):
    cog = MailSystem(bot)
    await bot.add_cog(cog)
