from .reportsystem import ReportSystem


async def setup(bot):
    reports = ReportSystem(bot)
    bot.add_cog(reports)
