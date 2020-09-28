from .core import MorseShark

async def setup(bot):
    bot.add_cog(MorseShark(bot))