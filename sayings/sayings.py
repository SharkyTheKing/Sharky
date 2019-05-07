import discord
import asyncio
from redbot.core import commands, checks
from redbot.core.data_manager import bundled_data_path

#----To Do----
#Add more people, add in the ability to set cooldown either incode or manully in Discord itself.


class Sayings(commands.Cog):
    """A list of People, Phrases, People from Red and hopefully more!"""
#People group
    @commands.group()
    async def people(self, ctx):
        """People"""
    
    @people.command()
    async def random(self, ctx):
        """Nothing to see here"""
        await ctx.send("What did I tell you? Nothing to see here!")

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
    
    @phrase.command()
    @checks.is_owner()
    @checks.admin()
    @checks.mod_or_permissions(manage_messages=True)
    async def error(self,ctx):
        """Don't use me!!"""
        async with ctx.typing():
            await ctx.send("Fuck, you broke me!")
            await asyncio.sleep(5)
            await ctx.send("Sike!")
            await asyncio.sleep(4)
            await ctx.send("Error: Sharky.exe Has Stopped Working")
            await asyncio.sleep(4)
            await ctx.send("....Adding fixes To Sharky.exe")
            await asyncio.sleep(4)
            await ctx.send("......Crash: Rebooting Sharky.exe")
            await asyncio.sleep(4)
            await ctx.send("....Failure Relaunching Sharky.exe")
            await asyncio.sleep(4)
            await ctx.send(".....Failure:Closing Sharky.exe")
            await asyncio.sleep(4)
            await ctx.send(".....Rebooting Sharky.exe")
            await asyncio.sleep(4)
            await ctx.send("...Confirmed Launching Sharky.exe")
            await asyncio.sleep(4)
            await ctx.send(".....Failure launching Sharky.exe")
            await asyncio.sleep(10)
            await ctx.send("...Launching Sharky.exe.....Failed: Exiting.")

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
            await ctx.send("Truly a badass Wyvern. Someone who make such a code that implodes your computer.")
    
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
    async def redbot(self, ctx):
        """Redbot"""
        await ctx.send("Should have, could have, would have*")
    
    @red.command()
    async def neuro(self, ctx):
        """Neuro"""
        await ctx.send("Fuck.")

    @red.command()
    async def will(self, ctx):
        """Will"""
        file = discord.File(str(bundled_data_path(self) / "will.png"))
        async with ctx.typing():
            await ctx.send("Will, the true master in the arts of trolling.", files=[file])
            asyncio.sleep(5)
            await ctx.send("and a really nice guy too")
        
    #Offiical Group
    @commands.group()
    async def fn(self, ctx):
        """Official Fortnite People"""

    @fn.command(name="sharky") #a way to add multiple subcommands with the same name
    async def sharky_fn(self, ctx):
        file = discord.File(str(bundled_data_path(self) / "sharky.png"))
        async with ctx.typing():
            await ctx.send("The fishy supermod", files=[file])
    
    @fn.command()
    async def deadman(self, ctx):
        file = discord.File(str(bundled_data_path(self) / "deadman.png"))
        async with ctx.typing():
            await ctx.send("The deadest of them all", files=[file])

    @fn.command()
    async def freak(self, ctx):
        """Currently nothing here"""
        await ctx.send("What did the info say? Nothing here you potato")
    
    @fn.command()
    async def ePoC(self, ctx):
        """ePoC????? wut"""
        async with ctx.typing():
            await asyncio.sleep(60)
            await ctx.send("wut...you waited a minute for this?")
    #adding more later
