import discord
from redbot.core import commands, checks
import asyncio


class SharkyTools(commands.Cog):
    """Sharky Tools"""

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
            member_role = ", ".join([x.name for x in member_role]) 
        joined = member.joined_at.strftime("%d %b %Y %H:%M")
        created = member.created_at.strftime("%d %b %Y %H:%M")     
        notice = "Puppy Shark"
    #   Embeds
        embed = discord.Embed(
            color=0xEE2222,
            title=f'{member_name}\'s information')
        embed.add_field(
            name='Name:',
            value=f'{member_mention}\n{member_name}#{member_disc}',
            inline=True)
        embed.add_field(
            name='ID:',
            value=f'{member_id}',
            inline=True)
        if member_bot is True:  # this is to define if a person is...well...a bot
            embed.add_field(
                name=('Bot:'),
                value=(f"{member_mention} is a bot"),
                inline=False)
        embed.add_field(
            name="Joined Date:",
            value=f'{joined}',
            inline=True)
        embed.add_field(
            name="Account Creation:",
            value=f'{created}',
            inline=True)
        embed.add_field(
            name='Roles:',
            value=f'{member_role}',
            inline=False)
        if member_voice and member_voice.channel: #this formats the voice call chunk into a proper message
            embed.add_field(
                name=("Current voice channel"),
                value="<#{0.id}> (ID: {0.id})".format(member_voice.channel),
                inline=False)
    # Non-fielded embedsets
    #    embed.set_image(url=member_avatar) - Ignore this entirely, just something extra
        embed.set_footer(
            text=f'{notice}')
        embed.set_thumbnail(
            url=member_avatar)
        embed.set_author(
            name=f'{member_name}#{member_disc}',
            icon_url=f'{member_avatar}')  
        await ctx.send(embed=embed)

#   Embed base = Trying to find if user is banned in Discord.
    @commands.command()
    @commands.bot_has_permissions(ban_members=True, embed_links=True, send_messages=True)  # Makes sure the bot has the proper permissions to do this command.
    @checks.mod_or_permissions(ban_members=True)  #  This makes sure a person has to be a mod or have ban_members permission to use.
    @commands.guild_only()
    async def findban(self, ctx, *, banneduser):
        """Check if a user is banned"""
        guild = ctx.guild  # Self explained
        bot = ctx.bot  # Self explained
        try:  # This tries to see if member works, if it doesn't it'll error out without this
            member = await bot.fetch_user(banneduser)  # Contains the bot.fetch_user
        except discord.NotFound:
            embed = discord.Embed(
                color=0xEE2222,
                title='Unknown User')
            embed.add_field(
                name=f'Not Valid',
                value=f'{banneduser} is not a Valid User\n Please make sure you\'re using a correct UserID.\nHow you ask? [Go here](https://support.discordapp.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-)')
            return await ctx.send(embed=embed)
        except discord.HTTPException:
            embed = discord.Embed(
                color=0xEE2222,
                title='Invalid Input')
            embed.add_field(
                name=f'ID10T Error:',
                value=f'**{banneduser}** is not a valid input...but you knew that, didn\'t you?')
            return await ctx.send(embed=embed)
        mid = banneduser
        hammer = 'https://cdn.discordapp.com/attachments/575846797709279262/578793294897741835/ban.png'
        #  This is where the command actually works. If a ban is found it'll output that it was found
        #   If the ban isn't found, it'll error and thus cause the discord.NotFound exception
        try:
            tban = await guild.fetch_ban(await bot.fetch_user(banneduser))
            #   embeds
            embed = discord.Embed(
                color=0xEE2222,
                title='Ban Found')
            embed.add_field(
                name=f'User Found:',
                value=f'{member}\n({mid})',
                inline=True)
            embed.add_field(
                name=f'Ban reason:',
                value=f'{tban[0]}',
                inline=False)
            embed.set_thumbnail(url=hammer)
            return await ctx.send(embed=embed)
        # Exception that if the person isn't found banned
        except discord.NotFound:
            embed = discord.Embed(color=0xEE2222, title='Ban **NOT** Found')
            embed.add_field(
                name=f'They are not banned from the server.', 
                value=f'{member} ({mid})')
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
        joined = user.joined_at.strftime("%d %b %Y %H:%M")
        created = user.created_at.strftime("%d %b %Y %H:%M")

        embed = discord.Embed(
            color=0xEE2222,
            title=f'Avatar Info'
        )
        embed.add_field(
            name=f'User Info:',
            value=f'{user_mention}\n({user_id})'
        )
        embed.add_field(
            name=f'Discord Name:',
            value=f'{user_name}#{user_disc}'
        )
        embed.add_field(
            name=f'Join Date:',
            value=f'{joined}'
        )
        embed.add_field(
            name=f'Account Age:',
            value=f'{created}'
        )
        embed.set_image(url=user_av)
        await ctx.send(embed=embed)

#   Fetching UserIDs for mobile users.
    @commands.command()
    @commands.guild_only()
    async def uid(self, ctx, *, user: discord.Member):
        """Get a user's ID"""
        u_id = user.id
        u_name = user.name
        await ctx.send(f'{u_name}\'s ID:\n{u_id}')
#   Guild ID
    @commands.command()
    @commands.guild_only()
    async def gid(self, ctx):
        """Guild ID? No problem"""
        guildid = ctx.guild.id
        await ctx.send(f'Guild\'s ID: {guildid}')
#   Format Bot Invites
    @commands.command()
    @commands.guild_only()
    async def binv(self, ctx, *, inv: discord.User):
        """
        Use a BOT's ID and it'll format it out into a link for you.
        It will DM it to you, incase the bot owner does not want their invite in public chatroom *yes that's ironic*.
        """
        bot_is = inv.bot
        bot_id = inv.id
        am = ctx.author.mention
        author = ctx.author
    
        if bot_is is True:
            return await author.send(f'https://discordapp.com/oauth2/authorize?client_id={bot_id}&scope=bot')
        await author.send(f"Try again {am}")
        try:
            await ctx.message.delete()
        except discord.errors.Forbidden:
            await ctx.send("``Error in command 'binv'. Check your console or logs for details.``")
            await asyncio.sleep(3)
            await ctx.send("Sike. Just fix your permissions")
