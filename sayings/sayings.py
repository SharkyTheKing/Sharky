import discord
from redbot.core import commands, checks
from redbot.core.data_manager import bundled_data_path
class Sayings(commands.Cog):
#People Group
    @commands.group()
    async def people(self, ctx):
        """People"""
    
    @people.command()
    async def soul(self, ctx):
        """A comment about Soul"""
        await ctx.send("Soul is a troll, for he is the king of them all. He's also an asshole.")
    
    @people.command()
    async def kowlin(self, ctx):
        """A comment about the Wyvern"""
        await ctx.send("Kowlin, for he is a lovely Wyvern who breaths fire, has your back and knows how to make shit look easy when it's really not.")

#phrase group
    @commands.group()
    async def phrase(self, ctx):
        """Phrases"""

    @phrase.command()
    async def potato(self, ctx):
        """Potatos"""
        await ctx.send("You are a potato.")

    @phrase.command()
    async def sharky(self, ctx):
        """Sharky"""
        await ctx.send("I see you, I see all, I know where you are and I know who you are. I am <@223391425302102016>")

    @phrase.command()
    async def gofish(self, ctx):
        """Definition of \"Go Fish\""""
        await ctx.send("Go fuck yourself")

#Red group
    @commands.group()
    async def red(self, ctx):
        """People from Red"""
    @red.command()
    async def kenny(self, ctx):
        """Kenny"""
        await ctx.send("A lovely person, with the best profile picture ever. Though his name makes you question if you're accidentally going to ping everyone....all the damn time")

    @red.command()
    async def flare(self, ctx):
        """Flare"""
        await ctx.send("The pikachu of them all, someone who makes you wonder how the hell does he fight a dargon? Magic? Strength? Or is he just too damn cute that the dargon doesn't like to hurt him....the world may never know.")

    @red.command()
    async def trusty(self, ctx):
        """Trusty"""
        file = discord.File(str(bundled_data_path(self) / "V4OLA-trustymeme.png")) #line 2 import, await ctx.send(files=[file]) is how it would send the file
        async with ctx.typing():
            await ctx.send("The type of guy who thought for some reason to put 'trust' in his name. Granted, everyone knows that doesn't make his trustworthy but it sure does make him a meme. His cogs also are known to break python itself, a true master of fucking with you.", files=[file])
        
    @red.command()
    async def flame(self, ctx):
        """Flame"""
        file = discord.File(str(bundled_data_path(self) / "flame.gif"))
        async with ctx.typing():
            await ctx.send("He's on fire!!!", files=[file])

    @red.command()
    async def kowlin(self, ctx):
        """Kowlin"""
        async with ctx.typing():
            await ctx.send("Awaiting input....")
    
    @red.command()
    async def jenn(self, ctx):
        """JennJenn"""
        file = discord.File(str(bundled_data_path(self) / "seppuku.png"))
        async with ctx.typing():
            await ctx.send("The powerful and knowledgeable Jenn. This is all that needs to be said of the greatness.", files=[file])

    @red.command()
    async def aika(self, ctx):
        """Aikaterna"""
        file = discord.File(str(bundled_data_path(self) / "catban.png"))
        async with ctx.typing():
            await ctx.send("Aik, the most powerful of the cats. For Aik swings the banhammer on all of those who oppose them.", files=[file])

    @red.command()
    async def red(self, ctx):
        async with ctx.typing():
            await ctx.send("Should have*")