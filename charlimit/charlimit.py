import discord
from redbot.core import commands, Config, checks
from redbot.core.bot import Red

BaseCog = getattr(commands, "Cog", object)


class Charlimit(BaseCog):  # Charrlimit! Get it?! Charr?! Ah fk... what do you know about humor.
    """Limit the amount of characters per channel"""

    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=98757087587)

        def_channel = {"channel": {"character_limit": None}}
        def_guild = {"message": False}
        self.config.register_channel(**def_channel)
        self.config.register_guild(**def_guild)

    @commands.guild_only()
    @commands.group()
    @checks.mod_or_permissions(manage_channels=True)
    async def charlimit(self, ctx):
        """Manage the character limits"""
        pass

    @charlimit.command()
    async def set(self, ctx, channel: discord.TextChannel, characters: int):
        """
        Sets the channel's character limit

        If you put 0 for a channel, it'll remove the character limit.
        `example: [p]charlimit set #general 0`
        """
        toggle = characters
        if characters == 0:
            await self.config.channel(channel).character_limit.set(None)
            await ctx.send(f"Done, cleared the character limit for {channel.mention}")
        else:
            await self.config.channel(channel).character_limit.set(characters)
            await ctx.send(f"Done, {channel.mention} is now set to {toggle} characters")

    @charlimit.command()
    async def message(self, ctx, toggle: bool):
        """
        Allows/Disallows the bot to send a message to users if they exceed the limit.

        Default is `False`, to allow type `[p]charlimit message True` othwerise no messages will be sent.
        """
        guild = ctx.guild
        config = self.config.guild(guild).message
        if toggle is True:
            await config.set(True)
            await ctx.send(
                "The bot will now message the users if they exceed the character limit."
            )
        elif toggle is False:
            await config.set(False)
            await ctx.send("The bot will not message the users.")

    #   The list of channels and their settings
    @charlimit.command()
    async def list(self, ctx):
        """
        The list of the channels in category and character limit
        """
        guild = ctx.guild
        message_conf = await self.config.guild(guild).message()
        count = ""
        for shark in ctx.guild.channels:
            characters = await self.config.channel(shark).character_limit()
            if characters is not None:
                count += f"{shark.mention}: {characters} characters\n"
            e = discord.Embed(color=guild.me.top_role.color)
            e.title = f"{guild}'s Settings"
            e.description = f"{count}"
            e.add_field(name="Exceeding Alert:", value=message_conf)
        return await ctx.send(embed=e)

    @commands.Cog.listener()
    async def on_message(self, message):
        current = message.channel
        guild = message.guild
        c_conf = await self.config.channel(current).character_limit()
        if c_conf is None:
            return False
        else:
            #   This has to be here or else it'll error out whenever someone DMs the bot.
            reason = f"Hey there, {message.author.name}.\n\nYour message in {current.mention} has been deleted due to you exceeding the {c_conf} character limit."
            if len(message.content) > c_conf:
                #   Check if the author is some sort of moderator.
                if (
                    current.permissions_for(message.author).manage_messages is True
                    or message.author.bot is True
                ):
                    return
                try:
                    await message.delete()
                    if await self.config.guild(guild).message() is True:
                        await message.author.send(reason)
                    else:
                        pass
                except discord.Forbidden:
                    pass
                except discord.AttributeError:
                    pass

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        await self.on_message(after)
