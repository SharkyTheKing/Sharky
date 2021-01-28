from .verification import Verify

__red_end_user_data_statement__ = (
    "This cog does not persistently store data or metadata about users."
)


async def setup(bot):
    cog = Verify(bot)
    bot.add_cog(cog)
    # noinspection PyProtectedMember
    await cog._maybe_update_config()
