import discord
from redbot.core import commands, checks
import asyncio
from redbot.core.utils.chat_formatting import pagify
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu
from redbot.core import bank
from typing import Sequence


class SharkyTools(commands.Cog):
    """Sharky Tools"""

    __author__ = "Sharky"
    __version__ = "2.0.4"

#  Sharky's Userinfo twist
    @commands.command(name="sharkinfo", aliases=['pinfo'])
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True, send_messages=True)
    async def sharkinfo(self, ctx, *, member: discord.Member = None):
        """
        User information with Sharky's twist
        """
        author = ctx.author
        if not member:
            member = author
        guild = ctx.guild
        member_mention = member.mention  # Mentions
        member_disc = member.discriminator  # The four digits
        member_name = member.name  # Default Discord name
        member_id = member.id  # USERID
        member_avatar = member.avatar_url_as(static_format="png")  # Avatar, static is formated as png
        member_voice = member.voice  # Tells us the voice chat they're in
        member_bot = member.bot
        member_role = sorted(member.roles, reverse=True)[:-1]  # this and line 35 are required for role formats
        if member_role:  # this lets us format the roles properly so theyr'e named correctly
            member_role = ", ".join([x.mention for x in member_role])  # Changed x.name to x.mention to ping the roles for color
        
        #  Tie this together with created_on and joined_on
        #  Credit to Red Core Userinfo command: I am not this smart yet :eyes:
        joined_at = member.joined_at  # This is REQUIRED for 'since_joined`
        member_joined = member.joined_at.strftime("%d %b %Y %H:%M")  # When the user joined the server
        since_joined = (ctx.message.created_at - joined_at).days  # Since the user joined the server in days
        member_created = member.created_at.strftime("%d %b %Y %H:%M")  # When the user account was created
        since_created = (ctx.message.created_at - member.created_at).days  # Since the user account was created in days

        created_on = ("{}\n({} days ago)").format(member_created, since_created)  # Formats when the account was created into a proper day message
        joined_on = ("{}\n({} days ago)").format(member_joined, since_joined)  # Formats when the account joined the server into a proper day message
        member_number = (sorted(guild.members, key=lambda m: m.joined_at or ctx.message.created_at).index(member) + 1)
        notice = f"Member #{member_number}"
        # This is to calculate the member count for the user
    #   Embeds
        embed = discord.Embed(color=0xEE2222, title=f'{member_name}\'s information')
        embed.add_field(name='Name:', value=f'{member_mention}\n{member_name}#{member_disc}', inline=True)
        embed.add_field(name='ID:', value=f'{member_id}', inline=True)
        if member_bot is True:  # this is to define if a person is...well...a bot
            embed.add_field(name='Bot:', value=f"{member_mention} is a bot", inline=False)
        embed.add_field(name="Account Creation:", value=f'{created_on}', inline=True)
        embed.add_field(name="Joined Date:", value=f'{joined_on}', inline=True)
        embed.add_field(name='Roles:', value=f'{member_role}', inline=False)
        if member_voice and member_voice.channel:  # this formats the voice call chunk into a proper message
            embed.add_field(name="Current voice channel", value="<#{0.id}> (ID: {0.id})".format(member_voice.channel), inline=False)
    # Non-fielded embedsets
        embed.set_footer(text=f'{notice}')
        embed.set_thumbnail(url=member_avatar)
        embed.set_author(name=f'{member_name}#{member_disc}', icon_url=f'{member_avatar}')  
        await ctx.send(embed=embed)

#   Trying to find if user is banned in Discord.
    @commands.command()
    @commands.bot_has_permissions(ban_members=True, embed_links=True, send_messages=True)  # Makes sure the bot has the proper permissions to do this command.
    @checks.mod_or_permissions(manage_messages=True)  #  This makes sure a person has to be a mod or have ban_members permission to use.
    @commands.guild_only()
    async def findban(self, ctx, *, banneduser):
        """Check if a user is banned"""
        guild = ctx.guild  # Self explained
        bot = ctx.bot  # Self explained
        try:  # This tries to see if member works, if it doesn't it'll error out without this
            member = await bot.fetch_user(banneduser)  # Contains the bot.fetch_user
        except discord.NotFound:
            embed = discord.Embed(color=0xEE2222, title='Unknown User')
            embed.add_field(name=f'Not Valid', value=f'{banneduser} is not a Valid User\n Please make sure you\'re using a correct UserID.\nHow you ask? [Go here](https://support.discordapp.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-)')
            return await ctx.send(embed=embed)
        except discord.HTTPException:
            embed = discord.Embed(color=0xEE2222, title='Invalid Input')
            embed.add_field(name='ID10T Error:', value=f'**{banneduser}** is not a valid input...but you knew that, didn\'t you?')
            return await ctx.send(embed=embed)
        mid = banneduser
        hammer = 'https://photos.kstj.us/TartPuzzlingKusimanse.png'
        x_emote = 'https://photos.kstj.us/GiddyDizzyIvorybilledwoodpecker.png'
        #  This is where the command actually works. If a ban is found it'll output that it was found
        #   If the ban isn't found, it'll error and thus cause the discord.NotFound exception
        try:
            tban = await guild.fetch_ban(await bot.fetch_user(banneduser))
            #   embeds
            embed = discord.Embed(color=0xEE2222, title='Ban Found')
            embed.add_field(name=f'User Found:', value=f'{member}\n({mid})', inline=True)
            embed.add_field(name=f'Ban reason:', value=f'{tban[0]}', inline=False)
            embed.set_thumbnail(url=hammer)
            return await ctx.send(embed=embed)
        # Exception that if the person isn't found banned
        except discord.NotFound:
            embed = discord.Embed(color=0xEE2222, title='Ban **NOT** Found')
            embed.add_field(
                name=f'They are not banned from the server.',
                value=f'{member} ({mid})')
            embed.set_thumbnail(url=x_emote)
            return await ctx.send(embed=embed)

#   User Avatar
    @commands.command()
    @commands.bot_has_permissions(embed_links=True, send_messages=True)
    @checks.mod_or_permissions(manage_messages=True)
    @commands.guild_only()
    async def av(self, ctx, *, user: discord.Member = None):
        """A user's avatar"""
        author = ctx.author
        if not user:
            user = author
        user_mention = user.mention  # Mentions
        user_disc = user.discriminator  # The four digits
        user_name = user.name  # Default Discord name
        user_id = user.id  # USERID
        user_av = user.avatar_url_as(static_format="png")  # Avatar, static is formated as png

        #  Tie this together with created_on and joined_on
        #  Credit to Red Core Userinfo command: I am not this smart yet :eyes:
        joined_at = user.joined_at  # This is REQUIRED for 'since_joined`
        user_joined = user.joined_at.strftime("%d %b %Y %H:%M")  # When the user joined the server
        since_joined = (ctx.message.created_at - joined_at).days  # Since the user joined the server in days
        user_created = user.created_at.strftime("%d %b %Y %H:%M")  # When the user account was created
        since_created = (ctx.message.created_at - user.created_at).days  # Since the user account was created in days

        created_on = ("{}\n({} days ago)").format(user_created, since_created)  # Formats when the account was created into a proper day message
        joined_on = ("{}\n({} days ago)").format(user_joined, since_joined)  # Formats when the account joined the server into a proper day message

        embed = discord.Embed(color=0xEE2222, title=f'Avatar Info')
        embed.add_field(name=f'User Info:', value=f'{user_mention}\n({user_id})')
        embed.add_field(name=f'Discord Name:', value=f'{user_name}#{user_disc}')
        embed.add_field(name=f'Account Age:', value=f'{created_on}')
        embed.add_field(name=f'Join Date:', value=f'{joined_on}')
        embed.set_image(url=user_av)
        await ctx.send(embed=embed)

# Grabbing ANY user's avatar. This is hidden on purpose
    @commands.command()
    @commands.bot_has_permissions(embed_links=True, send_messages=True)
    async def uav(self, ctx, *, user):
        """Get a user's avatar even if they aren't on the server"""
        author = ctx.author
        if not user:
            user = author
        try:
            #  argument setups
            user_acc = await ctx.bot.fetch_user(user)
            user_av = user_acc.avatar_url_as(static_format="png")
            user_name = user_acc.name
            user_disc = user_acc.discriminator
            #  embed
            embed = discord.Embed(color=0xEE2222, title=f'Avatar Info: {user_name}#{user_disc}')
            embed.set_image(url=user_av)
            await ctx.send(embed=embed)
        except discord.HTTPException:
            await ctx.send("Please use a valid UserID")

#   Fetching UserIDs for mobile users.
    @commands.command()
    @commands.guild_only()
    async def uid(self, ctx, *, user: discord.Member = None):
        """Get a user's ID"""
        author = ctx.author
        if not user:
            user = author
        u_id = user.id
        await ctx.send(f'{u_id}')
#   Guild ID
    @commands.command()
    @commands.guild_only()
    async def gid(self, ctx):
        """Guild ID? No problem"""
        guildid = ctx.guild.id
        await ctx.send(f'Guild\'s ID: {guildid}')

#   Format Bot Invites
    @checks.is_owner()
    @commands.guild_only()
    @commands.command()
    async def binv(self, ctx, *, inv: discord.User):
        """Get a bot's invite link by copying the ID of bot"""
        bot_is = inv.bot
        bot_id = inv.id
        author = ctx.author
        am = ctx.author.mention
        try:
            await ctx.message.delete()
            if bot_is is True:
                return await author.send(f'https://discordapp.com/oauth2/authorize?client_id={bot_id}&scope=bot')
            if bot_is is False:
                return await author.send(f"Try again {am}")
        except discord.errors.Forbidden:
            await ctx.send("Can't delete command message")

#  Find a user's account age and join age.
    @commands.guild_only()
    @commands.command()
    @commands.bot_has_permissions(embed_links=True, send_messages=True)
    async def age(self, ctx, *, user: discord.Member = None):
        """Find out the person's account age and join date!"""
        author = ctx.author
        if not user:
            user = author
        user_mention = user.mention
        user_name = user.name
        user_disc = user.discriminator
        user_av = user.avatar_url_as(static_format="png")
        joined_at = user.joined_at  # This is REQUIRED for 'since_joined`
        user_joined = user.joined_at.strftime("%d %b %Y %H:%M")  # When the user joined the server
        since_joined = (ctx.message.created_at - joined_at).days  # Since the user joined the server in days
        user_created = user.created_at.strftime("%d %b %Y %H:%M")  # When the user account was created
        since_created = (ctx.message.created_at - user.created_at).days  # Since the user account was created in days
        created_on = ("{}\n({} days ago)").format(user_created, since_created)  # Formats when the account was created into a proper day message
        joined_on = ("{}\n({} days ago)").format(user_joined, since_joined)  # Formats when the account joined the server into a proper day message

        bot_is = user.bot
        embed = discord.Embed(color=0xEE2222, title=f"{user_name}#{user_disc}'s Account Date:")
        embed.add_field(name=f'Account Age:', value=f'{created_on}')
        embed.add_field(name=f'Join Date:', value=f'{joined_on}')
        if bot_is is True:
            embed.add_field(name=f'Bot Found:', value=f'{user_mention} is a bot')
        embed.set_thumbnail(url=user_av)
        await ctx.send(embed=embed)
        
#   User menu, combinds most if not all of the commands together
    @commands.command(name="usermenu", aliases=['umenu', 'userm', 'um'])
    @commands.bot_has_permissions(embed_links=True, send_messages=True, add_reactions=True)
    @commands.guild_only()
    async def _umenu(self, ctx, *, member: discord.Member = None):
        """Ties all of the commands together, but in a menu! :D"""
        embeds = []

    # This is the list of definitions
        guild = ctx.guild
        author = ctx.author
        if not member:
            member = author
        member_mention = member.mention  # Mentions
        member_disc = member.discriminator  # The four digits
        member_name = member.name  # Default Discord name
        member_id = member.id  # USERID
        member_avatar = member.avatar_url_as(static_format="png")  # Avatar, static is formated as png
        member_voice = member.voice  # Tells us the voice chat they're in
        member_bot = member.bot

        member_role = sorted(member.roles, reverse=True)[:-1]  # this and if member_role are required for role formats
        if member_role:  # this lets us format the roles properly so theyr'e named correctly
            member_role = ", ".join([x.mention for x in member_role])
        else:
            member_role = None  # changed x.name to x.mention to make it ping the roles
        
        # bank stuff
        credits_name = await bank.get_currency_name(guild)
        bal = await bank.get_balance(member)
        
        #  Tie this together with created_on and joined_on
        #  Credit to Red Core Userinfo command: I am not this smart yet :eyes:
        joined_at = member.joined_at  # This is REQUIRED for 'since_joined`
        member_joined = member.joined_at.strftime("%d %b %Y %H:%M")  # When the user joined the server
        since_joined = (ctx.message.created_at - joined_at).days  # Since the user joined the server in days
        member_created = member.created_at.strftime("%d %b %Y %H:%M")  # When the user account was created
        since_created = (ctx.message.created_at - member.created_at).days  # Since the user account was created in days

        created_on = ("{}\n({} days ago)").format(member_created, since_created)  # Formats when the account was created into a proper day message
        joined_on = ("{}\n({} days ago)").format(member_joined, since_joined)  # Formats when the account joined the server into a proper day message
        member_number = (sorted(guild.members, key=lambda m: m.joined_at or ctx.message.created_at).index(member) + 1)
        notice = f"Member #{member_number}"
    # This is where the magic will hopefully happen
        for x in map(str, range(1, 4)):
            first = discord.Embed(
                color=0xEE2222,
                title=f'{member_name}\'s information')
            first.add_field(
                name='Name:',
                value=f'{member_mention}\n{member_name}#{member_disc}',
                inline=True)
            first.add_field(
                name='ID:',
                value=f'{member_id}',
                inline=True)
            if member_bot is True:  # this is to define if a person is...well...a bot
                first.add_field(
                    name=('Bot:'),
                    value=(f"{member_mention} is a bot"),
                    inline=False)
            if member_voice and member_voice.channel:  # this formats the voice call chunk into a proper message
                first.add_field(name="Current voice channel", value="<#{0.id}> (ID: {0.id})".format(member_voice.channel), inline=False)
            first.set_thumbnail(url=member_avatar)
            first.set_footer(text=f'{notice}')
            embeds.append(first)
            second = discord.Embed(color=0xEE2222, title=f'{member_name}\'s information')
            second.add_field(name="Account Creation:", value=f'{created_on}', inline=True)
            second.add_field(name="Joined Date:", value=f'{joined_on}', inline=True)
            if member_role is not None:
                second.add_field(name='Roles:', value=f'{member_role}', inline=False)
            second.set_thumbnail(url=member_avatar)
            second.set_footer(text=f'{notice}')
            embeds.append(second)
            third = discord.Embed(
                color=0xEE2222,
                title=f'{member_name}\'s Avatar')
            third.set_image(url=member_avatar)
            third.set_footer(text=f'{notice}')
            embeds.append(third)
            forth = discord.Embed(
                color=0XEE2222,
                title=f'Bank Balance'
            )
            forth.add_field(
                name=f"{member_name}'s Bank Statement",
                value=f'They have {bal}{credits_name} in their bank!'
            )
            forth.set_thumbnail(url=member_avatar)
            forth.set_footer(text=f'{notice}')
            embeds.append(forth)
        await menu(ctx, embeds, DEFAULT_CONTROLS)
#   Marking where TO PUT THE NEXT COMMAND. NOT DOWN THERE

#   Display Roles

    @commands.command()
    @commands.guild_only()
    async def roles(self, ctx):
        """Get the roles of the server\n\nCredit goes to [Trusty's Repo for SeverStats](https://github.com/TrustyJAID/Trusty-cogs) for the code"""
        guild = ctx.guild
        msg = ""
        for role in sorted(guild.roles, reverse=True):
            msg += f"{role.mention} ({len(role.members)})\n"
            msg_list = []
        for page in pagify(msg, ["\n"]):
            if ctx.channel.permissions_for(ctx.me).embed_links:
                embed = discord.Embed(color=0xEE2222)
                embed.description = page
                embed.set_author(name=guild.name + ("Roles"), icon_url=guild.icon_url)
                msg_list.append(embed)
        await menu(ctx, msg_list, DEFAULT_CONTROLS)