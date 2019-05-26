import discord
from redbot.core import commands, checks
import asyncio
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS
from redbot.core import bank
from typing import Sequence


class SharkyTools(commands.Cog):
    """Sharky Tools"""

    __author__ = "Sharky"
    __version__ = "2.0.0"

#  Sharky's Userinfo twist
    @commands.command(name="sharkinfo", aliases=['pinfo'])
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True, send_messages=True)
    async def sharkinfo(self, ctx, *, member: discord.Member):
        """
        User information with Sharky's twist
        """
        member_mention = member.mention  # Mentions
        member_disc = member.discriminator  # The four digits
        member_name = member.name  # Default Discord name
        member_id = member.id  # USERID
        member_avatar = member.avatar_url_as(static_format="png")  # Avatar, static is formated as png
        member_voice = member.voice  # Tells us the voice chat they're in
        member_bot = member.bot

        member_role = sorted(member.roles)[1:]  # this and line 35 are required for role formats
        if member_role:  # this lets us format the roles properly so theyr'e named correctly
            member_role = ", ".join([x.mention for x in member_role])  # Changed x.name to x.mention to ping the roles for color
        notice = "Puppy Shark"
        
        #  Tie this together with created_on and joined_on
        #  Credit to Red Core Userinfo command: I am not this smart yet :eyes:
        joined_at = member.joined_at  # This is REQUIRED for 'since_joined`
        member_joined = member.joined_at.strftime("%d %b %Y %H:%M")  # When the user joined the server
        since_joined = (ctx.message.created_at - joined_at).days  # Since the user joined the server in days
        member_created = member.created_at.strftime("%d %b %Y %H:%M")  # When the user account was created
        since_created = (ctx.message.created_at - member.created_at).days  # Since the user account was created in days

        created_on = ("{}\n({} days ago)").format(member_created, since_created)  # Formats when the account was created into a proper day message
        joined_on = ("{}\n({} days ago)").format(member_joined, since_joined)  # Formats when the account joined the server into a proper day message

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
    async def av(self, ctx, *, user: discord.Member):
        """A user's avatar"""
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
    async def uid(self, ctx, *, user: discord.Member):
        """Get a user's ID"""
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
    async def age(self, ctx, *, user: discord.Member):
        """Find out the person's account age and join date!"""
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
    async def _umenu(self, ctx, *, member: discord.Member):
        """Ties all of the commands together, but in a menu! :D"""
        embeds = []

    # This is the list of definitions
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
        credits_name = await bank.get_currency_name(ctx.guild)
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
            embeds.append(first)
            second = discord.Embed(color=0xEE2222, title=f'{member_name}\'s information')
            second.add_field(name="Account Creation:", value=f'{created_on}', inline=True)
            second.add_field(name="Joined Date:", value=f'{joined_on}', inline=True)
            if member_role is not None:
                second.add_field(name='Roles:', value=f'{member_role}', inline=False)
            second.set_thumbnail(url=member_avatar)
            embeds.append(second)
            third = discord.Embed(
                color=0xEE2222,
                title=f'{member_name}\'s Avatar')
            third.set_image(url=member_avatar)
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
            embeds.append(forth)
        await menu(ctx, embeds, DEFAULT_CONTROLS)
#   Marking where TO PUT THE NEXT COMMAND. NOT DOWN THERE

#   Display Roles *This took over 1k lines to account for max discord limits*

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True, send_messages=True, add_reactions=True)
    async def rolelist(self, ctx):
        """Role list command! \nActually accounts for Discord's maxium role creation limit.\n\n\nIf you complain about how it looks, you can fix it yourself this entire command alone took 1101 for this."""
        guild = ctx.guild
        r = sorted(guild.roles)[1:20]
        r2 = sorted(guild.roles)[21:40]
        r3 = sorted(guild.roles)[41:60]
        r4 = sorted(guild.roles)[61:80]
        r5 = sorted(guild.roles)[81:100]
        r6 = sorted(guild.roles)[101:120]
        r7 = sorted(guild.roles)[121:140]
        r8 = sorted(guild.roles)[141:160]
        r9 = sorted(guild.roles)[161:180]
        r10 = sorted(guild.roles)[181:200]
        r11 = sorted(guild.roles)[201:220]
        r12 = sorted(guild.roles)[221:240]
        r13 = sorted(guild.roles)[241:260]
        s = ", \n".join([x.mention for x in r])
        s2 = ", \n".join([x.mention for x in r2])
        s3 = ", \n".join([x.mention for x in r3])
        s4 = ", \n".join([x.mention for x in r4])
        s5 = ", \n".join([x.mention for x in r5])
        s6 = ", \n".join([x.mention for x in r6])
        s7 = ", \n".join([x.mention for x in r7])
        s8 = ", \n".join([x.mention for x in r8])
        s9 = ", \n".join([x.mention for x in r9])
        s10 = ", \n".join([x.mention for x in r10])
        s11 = ", \n".join([x.mention for x in r11])
        s12 = ", \n".join([x.mention for x in r12])
        s13 = ", \n".join([x.mention for x in r13])
        if len(guild.roles) < 20:
            await ctx.maybe_send_embed(s)
        elif 21 < len(guild.roles) < 40:
            embeds = []
            for x in map(str, range(1, 4)):

                a = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                a.add_field(
                    name='Guild\'s Roles',
                    value=f'{s}'
                )
                a.set_footer(
                    text="Page 1")
                embeds.append(a)

                b = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                b.add_field(
                    name="Guild's Roles",
                    value=f'{s2}'
                )
                b.set_footer(
                    text="Page 2")
                embeds.append(b)
            await menu(ctx, embeds, DEFAULT_CONTROLS)
        elif 41 < len(guild.roles) < 60:
            embeds = []
            for x in map(str, range(1, 4)):
                a = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                a.add_field(
                    name='Guild\'s Roles',
                    value=f'{s}'
                )
                a.set_footer(
                    text="Page 1")
                embeds.append(a)
                b = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                b.add_field(
                    name="Guild's Roles",
                    value=f'{s2}'
                )
                b.set_footer(
                    text="Page 2")
                embeds.append(b)
                c = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                c.add_field(
                    name="Guild's Roles",
                    value=f'{s3}'
                )
                c.set_footer(
                    text="Page 3")
                embeds.append(c)
            await menu(ctx, embeds, DEFAULT_CONTROLS)
        #   Seperation
        elif 61 < len(guild.roles) < 80:
            embeds = []
            for x in map(str, range(1, 4)):
                a = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                a.add_field(
                    name='Guild\'s Roles',
                    value=f'{s}'
                )
                a.set_footer(
                    text="Page 1")
                embeds.append(a)

                b = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                b.add_field(
                    name="Guild's Roles",
                    value=f'{s2}'
                )
                b.set_footer(
                    text="Page 2")
                embeds.append(b)
                c = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                c.add_field(
                    name="Guild's Roles",
                    value=f'{s3}'
                )
                c.set_footer(
                    text="Page 3")
                embeds.append(c)
                d = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                d.add_field(
                    name="Guild's Roles",
                    value=f'{s4}'
                )
                d.set_footer(
                    text="Page 4")
                embeds.append(d)
            await menu(ctx, embeds, DEFAULT_CONTROLS)
        elif 81 < len(guild.roles) < 100:
            embeds = []
            for x in map(str, range(1, 10)):
                a = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                a.add_field(
                    name='Guild\'s Roles',
                    value=f'{s}'
                )
                a.set_footer(
                    text="Page 1")
                embeds.append(a)

                b = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                b.add_field(
                    name="Guild's Roles",
                    value=f'{s2}'
                )
                b.set_footer(
                    text="Page 2")
                embeds.append(b)
                c = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                c.add_field(
                    name="Guild's Roles",
                    value=f'{s3}'
                )
                c.set_footer(
                    text="Page 3")
                embeds.append(c)
                d = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                d.add_field(
                    name="Guild's Roles",
                    value=f'{s4}'
                )
                d.set_footer(
                    text="Page 4")
                embeds.append(d)
                e = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                e.add_field(
                    name="Guild's Roles",
                    value=f'{s5}'
                )
                e.set_footer(
                    text="Page 5")
                embeds.append(e)
            await menu(ctx, embeds, DEFAULT_CONTROLS)
        elif 101 < len(guild.roles) < 120:
            embeds = []
            for x in map(str, range(1, 10)):
                a = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                a.add_field(
                    name='Guild\'s Roles',
                    value=f'{s}'
                )
                a.set_footer(
                    text="Page 1")
                embeds.append(a)

                b = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                b.add_field(
                    name="Guild's Roles",
                    value=f'{s2}'
                )
                b.set_footer(
                    text="Page 2")
                embeds.append(b)
                c = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                c.add_field(
                    name="Guild's Roles",
                    value=f'{s3}'
                )
                c.set_footer(
                    text="Page 3")
                embeds.append(c)
                d = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                d.add_field(
                    name="Guild's Roles",
                    value=f'{s4}'
                )
                d.set_footer(
                    text="Page 4")
                embeds.append(d)
                e = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                e.add_field(
                    name="Guild's Roles",
                    value=f'{s5}'
                )
                e.set_footer(
                    text="Page 5")
                embeds.append(e)
                f = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                f.add_field(
                    name="Guild's Roles",
                    value=f'{s6}'
                )
                f.set_footer(
                    text="Page 6")
                embeds.append(f)
            await menu(ctx, embeds, DEFAULT_CONTROLS)
        elif 121 < len(guild.roles) < 140:
            embeds = []
            for x in map(str, range(1, 10)):
                a = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                a.add_field(
                    name='Guild\'s Roles',
                    value=f'{s}'
                )
                a.set_footer(
                    text="Page 1")
                embeds.append(a)

                b = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                b.add_field(
                    name="Guild's Roles",
                    value=f'{s2}'
                )
                b.set_footer(
                    text="Page 2")
                embeds.append(b)
                c = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                c.add_field(
                    name="Guild's Roles",
                    value=f'{s3}'
                )
                c.set_footer(
                    text="Page 3")
                embeds.append(c)
                d = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                d.add_field(
                    name="Guild's Roles",
                    value=f'{s4}'
                )
                d.set_footer(
                    text="Page 4")
                embeds.append(d)
                e = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                e.add_field(
                    name="Guild's Roles",
                    value=f'{s5}'
                )
                e.set_footer(
                    text="Page 5")
                embeds.append(e)
                f = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                f.add_field(
                    name="Guild's Roles",
                    value=f'{s6}'
                )
                f.set_footer(
                    text="Page 6")
                embeds.append(f)
                g = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                g.add_field(
                    name="Guild's Roles",
                    value=f'{s7}'
                )
                g.set_footer(
                    text="Page 7")
                embeds.append(g)
            await menu(ctx, embeds, DEFAULT_CONTROLS)
        elif 141 < len(guild.roles) < 160:
            embeds = []
            for x in map(str, range(1, 10)):
                a = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                a.add_field(
                    name='Guild\'s Roles',
                    value=f'{s}'
                )
                a.set_footer(
                    text="Page 1")
                embeds.append(a)

                b = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                b.add_field(
                    name="Guild's Roles",
                    value=f'{s2}'
                )
                b.set_footer(
                    text="Page 2")
                embeds.append(b)
                c = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                c.add_field(
                    name="Guild's Roles",
                    value=f'{s3}'
                )
                c.set_footer(
                    text="Page 3")
                embeds.append(c)
                d = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                d.add_field(
                    name="Guild's Roles",
                    value=f'{s4}'
                )
                d.set_footer(
                    text="Page 4")
                embeds.append(d)
                e = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                e.add_field(
                    name="Guild's Roles",
                    value=f'{s5}'
                )
                e.set_footer(
                    text="Page 5")
                embeds.append(e)
                f = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                f.add_field(
                    name="Guild's Roles",
                    value=f'{s6}'
                )
                f.set_footer(
                    text="Page 6")
                embeds.append(f)
                g = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                g.add_field(
                    name="Guild's Roles",
                    value=f'{s7}'
                )
                g.set_footer(
                    text="Page 7")
                embeds.append(g)
                h = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                h.add_field(
                    name="Guild's Roles",
                    value=f'{s8}'
                )
                h.set_footer(
                    text="Page 8")
                embeds.append(h)
            await menu(ctx, embeds, DEFAULT_CONTROLS)
        elif 161 < len(guild.roles) < 180:
            embeds = []
            for x in map(str, range(1, 10)):
                a = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                a.add_field(
                    name='Guild\'s Roles',
                    value=f'{s}'
                )
                a.set_footer(
                    text="Page 1")
                embeds.append(a)

                b = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                b.add_field(
                    name="Guild's Roles",
                    value=f'{s2}'
                )
                b.set_footer(
                    text="Page 2")
                embeds.append(b)
                c = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                c.add_field(
                    name="Guild's Roles",
                    value=f'{s3}'
                )
                c.set_footer(
                    text="Page 3")
                embeds.append(c)
                d = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                d.add_field(
                    name="Guild's Roles",
                    value=f'{s4}'
                )
                d.set_footer(
                    text="Page 4")
                embeds.append(d)
                e = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                e.add_field(
                    name="Guild's Roles",
                    value=f'{s5}'
                )
                e.set_footer(
                    text="Page 5")
                embeds.append(e)
                f = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                f.add_field(
                    name="Guild's Roles",
                    value=f'{s6}'
                )
                f.set_footer(
                    text="Page 6")
                embeds.append(f)
                g = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                g.add_field(
                    name="Guild's Roles",
                    value=f'{s7}'
                )
                g.set_footer(
                    text="Page 7")
                embeds.append(g)
                h = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                h.add_field(
                    name="Guild's Roles",
                    value=f'{s8}'
                )
                h.set_footer(
                    text="Page 8")
                embeds.append(h)
                i = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                i.add_field(
                    name="Guild's Roles",
                    value=f'{s9}'
                )
                i.set_footer(
                    text="Page 9"
                )
                embeds.append(i)
            await menu(ctx, embeds, DEFAULT_CONTROLS)
        elif 181 < len(guild.roles) < 200:
            embeds = []
            for x in map(str, range(1, 10)):
                a = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                a.add_field(
                    name='Guild\'s Roles',
                    value=f'{s}'
                )
                a.set_footer(
                    text="Page 1")
                embeds.append(a)

                b = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                b.add_field(
                    name="Guild's Roles",
                    value=f'{s2}'
                )
                b.set_footer(
                    text="Page 2")
                embeds.append(b)
                c = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                c.add_field(
                    name="Guild's Roles",
                    value=f'{s3}'
                )
                c.set_footer(
                    text="Page 3")
                embeds.append(c)
                d = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                d.add_field(
                    name="Guild's Roles",
                    value=f'{s4}'
                )
                d.set_footer(
                    text="Page 4")
                embeds.append(d)
                e = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                e.add_field(
                    name="Guild's Roles",
                    value=f'{s5}'
                )
                e.set_footer(
                    text="Page 5")
                embeds.append(e)
                f = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                f.add_field(
                    name="Guild's Roles",
                    value=f'{s6}'
                )
                f.set_footer(
                    text="Page 6")
                embeds.append(f)
                g = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                g.add_field(
                    name="Guild's Roles",
                    value=f'{s7}'
                )
                g.set_footer(
                    text="Page 7")
                embeds.append(g)
                h = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                h.add_field(
                    name="Guild's Roles",
                    value=f'{s8}'
                )
                h.set_footer(
                    text="Page 8")
                embeds.append(h)
                i = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                i.add_field(
                    name="Guild's Roles",
                    value=f'{s9}'
                )
                i.set_footer(
                    text="Page 9"
                )
                embeds.append(i)
                j = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                j.add_field(
                    name="Guild's Roles",
                    value=f'{s10}'
                )
                j.set_footer(
                    text="Page 10"
                )
                embeds.append(j)
            await menu(ctx, embeds, DEFAULT_CONTROLS)
        elif 201 < len(guild.roles) < 220:
            embeds = []
            for x in map(str, range(1, 10)):
                a = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                a.add_field(
                    name='Guild\'s Roles',
                    value=f'{s}'
                )
                a.set_footer(
                    text="Page 1")
                embeds.append(a)

                b = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                b.add_field(
                    name="Guild's Roles",
                    value=f'{s2}'
                )
                b.set_footer(
                    text="Page 2")
                embeds.append(b)
                c = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                c.add_field(
                    name="Guild's Roles",
                    value=f'{s3}'
                )
                c.set_footer(
                    text="Page 3")
                embeds.append(c)
                d = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                d.add_field(
                    name="Guild's Roles",
                    value=f'{s4}'
                )
                d.set_footer(
                    text="Page 4")
                embeds.append(d)
                e = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                e.add_field(
                    name="Guild's Roles",
                    value=f'{s5}'
                )
                e.set_footer(
                    text="Page 5")
                embeds.append(e)
                f = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                f.add_field(
                    name="Guild's Roles",
                    value=f'{s6}'
                )
                f.set_footer(
                    text="Page 6")
                embeds.append(f)
                g = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                g.add_field(
                    name="Guild's Roles",
                    value=f'{s7}'
                )
                g.set_footer(
                    text="Page 7")
                embeds.append(g)
                h = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                h.add_field(
                    name="Guild's Roles",
                    value=f'{s8}'
                )
                h.set_footer(
                    text="Page 8")
                embeds.append(h)
                i = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                i.add_field(
                    name="Guild's Roles",
                    value=f'{s9}'
                )
                i.set_footer(
                    text="Page 9"
                )
                embeds.append(i)
                j = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                j.add_field(
                    name="Guild's Roles",
                    value=f'{s10}'
                )
                j.set_footer(
                    text="Page 10"
                )
                embeds.append(j)
                k = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                k.add_field(
                    name="Guild's Roles",
                    value=f'{s11}'
                )
                k.set_footer(
                    text="Page 11"
                )
                embeds.append(k)
            await menu(ctx, embeds, DEFAULT_CONTROLS)
        elif 221 < len(guild.roles) < 240:
            embeds = []
            for x in map(str, range(1, 10)):
                a = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                a.add_field(
                    name='Guild\'s Roles',
                    value=f'{s}'
                )
                a.set_footer(
                    text="Page 1")
                embeds.append(a)

                b = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                b.add_field(
                    name="Guild's Roles",
                    value=f'{s2}'
                )
                b.set_footer(
                    text="Page 2")
                embeds.append(b)
                c = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                c.add_field(
                    name="Guild's Roles",
                    value=f'{s3}'
                )
                c.set_footer(
                    text="Page 3")
                embeds.append(c)
                d = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                d.add_field(
                    name="Guild's Roles",
                    value=f'{s4}'
                )
                d.set_footer(
                    text="Page 4")
                embeds.append(d)
                e = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                e.add_field(
                    name="Guild's Roles",
                    value=f'{s5}'
                )
                e.set_footer(
                    text="Page 5")
                embeds.append(e)
                f = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                f.add_field(
                    name="Guild's Roles",
                    value=f'{s6}'
                )
                f.set_footer(
                    text="Page 6")
                embeds.append(f)
                g = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                g.add_field(
                    name="Guild's Roles",
                    value=f'{s7}'
                )
                g.set_footer(
                    text="Page 7")
                embeds.append(g)
                h = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                h.add_field(
                    name="Guild's Roles",
                    value=f'{s8}'
                )
                h.set_footer(
                    text="Page 8")
                embeds.append(h)
                i = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                i.add_field(
                    name="Guild's Roles",
                    value=f'{s9}'
                )
                i.set_footer(
                    text="Page 9"
                )
                embeds.append(i)
                j = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                j.add_field(
                    name="Guild's Roles",
                    value=f'{s10}'
                )
                j.set_footer(
                    text="Page 10"
                )
                embeds.append(j)
                k = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                k.add_field(
                    name="Guild's Roles",
                    value=f"{s11}"
                )
                k.set_footer(
                    text="Page 11"
                )
                embeds.append(k)
                l = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                l.add_field(
                    name="Guild's Roles",
                    value=f'{s12}'
                )
                l.set_footer(
                    text="Page 12"
                )
                embeds.append(l)
            await menu(ctx, embeds, DEFAULT_CONTROLS)
        elif 241 < len(guild.roles) < 260:
            embeds = []
            for x in map(str, range(1, 10)):
                a = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                a.add_field(
                    name='Guild\'s Roles',
                    value=f'{s}'
                )
                a.set_footer(
                    text="Page 1")
                embeds.append(a)

                b = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                b.add_field(
                    name="Guild's Roles",
                    value=f'{s2}'
                )
                b.set_footer(
                    text="Page 2")
                embeds.append(b)
                c = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                c.add_field(
                    name="Guild's Roles",
                    value=f'{s3}'
                )
                c.set_footer(
                    text="Page 3")
                embeds.append(c)
                d = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                d.add_field(
                    name="Guild's Roles",
                    value=f'{s4}'
                )
                d.set_footer(
                    text="Page 4")
                embeds.append(d)
                e = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                e.add_field(
                    name="Guild's Roles",
                    value=f'{s5}'
                )
                e.set_footer(
                    text="Page 5")
                embeds.append(e)
                f = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                f.add_field(
                    name="Guild's Roles",
                    value=f'{s6}'
                )
                f.set_footer(
                    text="Page 6")
                embeds.append(f)
                g = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                g.add_field(
                    name="Guild's Roles",
                    value=f'{s7}'
                )
                g.set_footer(
                    text="Page 7")
                embeds.append(g)
                h = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                h.add_field(
                    name="Guild's Roles",
                    value=f'{s8}'
                )
                h.set_footer(
                    text="Page 8")
                embeds.append(h)
                i = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                i.add_field(
                    name="Guild's Roles",
                    value=f'{s9}'
                )
                i.set_footer(
                    text="Page 9"
                )
                embeds.append(i)
                j = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                j.add_field(
                    name="Guild's Roles",
                    value=f'{s10}'
                )
                j.set_footer(
                    text="Page 10"
                )
                embeds.append(j)
                k = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                k.add_field(
                    name="Guild's Roles",
                    value=f'{s11}'
                )
                k.set_footer(
                    text="Page 11"
                )
                embeds.append(k)
                l = discord.Embed(
                    color=0xEE2222,
                    title="Server's Info"
                )
                l.add_field(
                    name="Guild's Roles",
                    value=f'{s12}'
                )
                l.set_footer(text="Page 12")
                embeds.append(l)

                m = discord.Embed(color=0xEE2222, title="Server's Info")
                m.add_field(name="Guild's Roles", value=f'{s13}')
                m.set_footer(text="Page 13")
                embeds.append(m)
            await menu(ctx, embeds, DEFAULT_CONTROLS)
    #   If you somehow got down here. Why? Don't ever do this. Don't be like sharky.