import discord
import asyncio
from redbot.core import commands, checks
from redbot.core.data_manager import bundled_data_path
from redbot.core.utils.chat_formatting import box
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS
from redbot.core import bank
from redbot.core.utils.chat_formatting import pagify

class Learning(commands.Cog):
    """Learning the differnt ways of doing stuff\nA lot of these is taken part from [RedJumpMan](https://github.com/Redjumpman/Jumper-Plugins/wiki/Red-Coding-Guide-V3)"""

#This requires to do line 5 > from redbot.core.utils.chat_formating import box
    @commands.command()
    async def boxformat(self, ctx, *, message):
        """Markdown Testing\nCurrently there's no language specfic type set. Testing this out."""
        await ctx.send(box(message)) #if you add ,lang 'py' it'll format the text into python codeblock


    @commands.command()
    async def text(self, ctx):
        """Same as boxformat but preset text and language"""
        message = "Testing this out, very lovely numbers 123 46 928 20380 and 234."
        await ctx.send(box(message, lang='py'))

#this only requires import discord and you can only use userIDs to find the person.
    @commands.command()
    async def findmember(self, ctx, member_id: int):
        """Can find a member in the server, needs to have USERID. Looking at docs later"""
        member = discord.utils.get(ctx.guild.members, id=member_id)
        joined = member.joined_at.strftime("%d %b %Y %H:%M")
        if member:
            return await ctx.send(f'{member.name} was found. They joined {joined}')
        await ctx.send(f'No member on the server match the id: {member_id}.')
    
#this requires to have asyncio imported as per line 2
#Idea: Learn datetime or whatever it is, to get this to tell me the current time.
    @commands.command() 
    async def edittest(self, ctx):
        """Edit a cute message"""
        async with ctx.typing():
            message = await ctx.send("Hello World")
            await asyncio.sleep(5)
            await message.edit(content="Goodbye World") #in order to edit. you MUST contain content="" 


    @commands.command() 
    async def edit(self, ctx, message, message2):
        """Edit message!\n\nRemember to contain each message with a quotation.\nExample: \"Goodmorning, it\'s nice out today\" \"Yes, yes it is\""""
        async with ctx.typing():
            sending = await ctx.send(message)
            await asyncio.sleep(3)
            await sending.edit(content=message2)


#How to make a simple embed
    @commands.command()
    async def embedtest(self, ctx, *, message):
        """Embed testing"""
        text = "This is just here a placeholder, if you replace \"message\" with \"text\" you'll send that instead of what you input."
        await ctx.maybe_send_embed(message)

#How to make a more...advanced embed?
    @commands.command()
    async def embedtest2(self, ctx):
        embed = discord.Embed(color=0xEE2222, title='New Embed')
        embed.add_field(name='title 1', value='value 1')
        embed.add_field(name='title 2', value='value 2')
        embed.set_footer(text='I am the footer!')   
        await ctx.send(embed=embed)

#This requires to import menu. as per line 6: from redbot.core.utils.menus import menu, DEFAULT_CONTROLS
    @commands.command()
    async def menu(self, ctx):
        """Menu testing 1, this is text format"""
        pages = ["page 1", "page 2", "page 3"]  # or use pagify to split a long string.
        await menu(ctx, pages, DEFAULT_CONTROLS)
#Same as above, though this one is in text format 
    @commands.command()
    async def menu2(self, ctx):
        """Menu Testing 2, this is embed format"""
        embeds = []
        for x in map(str, range(1, 4)):
            embed = discord.Embed(color=0xEE2222, title=f"Page {x}")
            embeds.append(embed)
        await menu(ctx, embeds, DEFAULT_CONTROLS)

#Only requires importing discord. This is how to find when someone joined a server and created their account
    @commands.command()
    async def joined(self, ctx, member: discord.Member): #Use this later and take into line 27
        """When someone joined"""
        joined = member.joined_at.strftime("%d %b %Y %H:%M")
        created = member.created_at.strftime("%d %b %Y %H:%M")
        msg = (f'Join date for {member.mention}: {joined}\n'
            f'Account created on: {created}')
        await ctx.maybe_send_embed(msg) #Changed this into sending a embed, 'maybe_send_embed'

#This is how you check if someone is an owner, admin, mod or not.
    @commands.command()
    @checks.is_owner()
    async def checkowner(self, ctx):
        await ctx.send("I can only be used by the bot owner.")

    @commands.command()
    @checks.admin_or_permissions(ban_members=True)
    async def checkadmin(self, ctx):
        await ctx.send("I require an admin or someone with the \"ban members\" permission to be used")

    @commands.command()
    @checks.mod_or_permissions(manage_messages=True)
    async def checkmod(self, ctx):
        await ctx.send("I require a mod or someone with the \"manage_message\" permission to be used")

#This command lock makes it so the command can only be used in a guild
    @commands.command()
    @commands.guild_only()
    async def guildonly(self, ctx):
        """Guild only"""
        await ctx.send("I can only be used in a guild!")

#This command requires line 7, fromt redbot.core import bank to interact with the economy/bank
    @commands.command()
    @commands.guild_only()
    async def richornah(self, ctx):
        """Are you rich? Are you poor? find out!"""
        balance = await bank.get_balance(ctx.author)
        currency_name = await bank.get_currency_name(ctx.guild)
        if balance > 10000:
            await ctx.send (f"You are rich!\nYou have {balance}{currency_name}! Congratulations!")
        else:
            await ctx.send(f"Looks like you are running low on funds. You have {balance}{currency_name}, you need 10k or more to be rich!")
        
#Reference to my other cog on my repo https://github.com/SharkyTheKing/Sharky
    @commands.command()
    async def cooldowns(self, ctx):
        """Information reference"""
        x = '[repo, to learn more about cooldowns!](https://github.com/SharkyTheKing/Sharky)'
        await ctx.maybe_send_embed(f"I've always made a reference to this, please refer to cog \"cooldown\" on my {x}")

    @checks.is_owner()
    @commands.command() #How to go pass the 2k limit
    async def characterbypass(self, ctx): #from redbot.core.utils.chat_formatting import pagify as per line 8
    # The length of msg will be 2500 characters
        msg = 'I am over 2000 characters' * 100
        for page in pagify(msg):
            await ctx.send(page)

    @commands.command() #Message interactively
    async def interlimit(self, ctx):
    # The length of msg will be 2500 characters
        msg = 'I am over 2000 characters' * 100
        await ctx.send_interactive(pagify(msg))

    @commands.command(name="roles", hidden=True)
    async def _roles(self, ctx):
        """Testing"""
        guild = ctx.guild
        r = sorted(guild.roles)[1:]
        s = ", \n".join([x.mention for x in r])
        embeds = []
        embed = discord.Embed(
                color=0xEE2222,
                description=f'information\n{s}')
        embeds.append(embed)
        shits = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        curpage = 0
        for shit in shits:
            curpage += 1
            embed = discord.Embed(description=f"Page {curpage}/{len(shits)}")
        embeds.append(embed)
        await ctx.send(embed=embed)


#How to add aliases to commands
    #@commands.command(name="list", aliases=['ls', 'data', 'total'])
    #async def _list(self, ctx):
    #    await ctx.send("I can be called with `list`, `ls`, `data` and `total`.")

#How to go pass the 2k limit
    #How can I send a message over 2000 characters?

    #API REFERENCE: Pagify

    #Trying to send a message that is over 2000 characters in length will result in a HTTPException error being raised. In order to circumvent this restriction, you must split the message into chunks that do not exceed the limit. Red provides a utility called pagify to make this easy for you.

    
    #Import this from the top "from redbot.core.utils.chat_formatting import pagify"
    
    #@commands.command()
    #async def cmd(self, ctx):
        # The length of msg will be 2500 characters
    #    msg = 'I am over 2000 characters' * 100
    #    for page in pagify(msg):
    #        await ctx.send(page)

#How to send a message interactively

    #How can I send multiple messages interactively?

    #API Reference: Interactive Messages

    #Red provides a great utility in ctx that allows the user to control the flow of messages that are over 2000 characters. While the pagify utility can be great on it's own, the send_interactivewill allow the user to control the flow.

    #from redbot.core.utils.chat_formatting import pagify

    #@commands.command()
    #async def cmd(self, ctx):
        # The length of msg will be 2500 characters
    #    msg = 'I am over 2000 characters' * 100
    #    await ctx.send_interactive(pagify(msg))

#How to trigger when someone joins my server
    #async def on_member_join(self, member):
    #    server = member.guild.name
    #    await member.send(f"Welcome to {server}.")