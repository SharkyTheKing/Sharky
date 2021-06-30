from .modmail import MailSystem


async def setup(bot):
    cog = MailSystem(bot)
    bot.add_cog(cog)
