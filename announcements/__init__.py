from .announcements import Announcements


def setup(bot):
    bot.add_cog(Announcements(bot))
