import discord
from redbot.core import commands, Config, checks
from redbot.core.utils.chat_formatting import box, pagify

import re
from typing import Optional

BaseCog = getattr(commands, "Cog", object)

#  TODO Possibly setup channel specific filtering
#      TODO if this is done, need to look into making sure you can check each channel's filters
#  TODO Cleanup on_message and descriptin_help for each command


class FilterSystem(BaseCog):
    """
    Filter stuff here!

    You can only filter something one at a time, if you filter something, it'll take the whole filter into context...so don't filter the fucking letter x
    This can't be used with the CORE filter system as this uses the commands based off of it.
    """

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=2398472689223426)

        def_guild = {"logs": None, "filtered": [], "strict_filtered": [], "whitelist": []}
        self.config.register_guild(**def_guild)

    @commands.guild_only()
    @commands.group(pass_context=True)
    @checks.mod_or_permissions(manage_messages=True)
    async def filter(self, ctx):
        """
        Filter system
        """
        if ctx.invoked_subcommand is None:
            pass

    @filter.command()
    async def list(self, ctx):
        guild = ctx.guild
        author = ctx.author
        filters = await self.config.guild(guild).filtered()
        strict = await self.config.guild(guild).strict_filtered()
        whitelist = await self.config.guild(guild).whitelist()
        amount = ""
        msg = ""
        if filters and strict and whitelist is None:
            return False
        if filters:
            words = ", ".join(filters)
        else:
            words = "No filtered added"
        if strict:
            word_2 = ", ".join(strict)
        else:
            word_2 = "No strict filtered added"
        if whitelist:
            word_3 = ", ".join(whitelist)
        else:
            word_3 = "No whitelisted words added"
        msg += f"Current Channels:\n{amount}"
        words = (
            ("Filtered in this server:\n")
            + "```"
            + words
            + "```\n"
            + ("Strict Filtered in this server:\n")
            + "```"
            + word_2
            + "```\n"
            + ("Whitelisted in this server:\n")
            + "```"
            + word_3
            + "```"
        )
        try:
            for page in pagify(words, delims=[" ", "\n"], shorten_by=8):
                await author.send(page)
        except discord.Forbidden:
            await ctx.send("I can't send direct messages to you.")

    @filter.command()
    @checks.mod_or_permissions(manage_messages=True)
    async def logging(self, ctx, channel: Optional[discord.TextChannel]):
        """
        Sets the logging channel

        If no input is given it'll clear the channel
        """
        guild = ctx.guild
        log = self.config.guild(guild).logs
        if channel is None:
            await log.clear()
            await ctx.send("Cleared the logging channel")
        else:
            await log.set(channel.id)
            await ctx.send("Set the current logging channel to {}".format(channel.mention))

    @filter.command()
    async def add(self, ctx, *, word: str):
        """
        Add a word to the filter system
        """
        guild = ctx.guild
        adding_word = word.lower()
        if adding_word not in await self.config.guild(guild).filtered():
            async with self.config.guild(guild).filtered() as more:
                more.append(adding_word)
            await ctx.send("Added {} to the filter".format(word))
        else:
            await ctx.send("{} is already in the filter".format(word))

    @filter.command()
    async def remove(self, ctx, *, word: str):
        """
        Removes a word from the filter system
        """
        guild = ctx.guild
        removal_word = word
        if removal_word in await self.config.guild(guild).filtered():
            async with self.config.guild(guild).filtered() as less:
                less.remove(removal_word)
            await ctx.send("Removed {} from the filter".format(word))
        else:
            await ctx.send("{} is not in the filter".format(word))

    @filter.command()
    async def strict(self, ctx, *, word: str):
        """
        Adds/Removes a word that is being watched for the EXACT
        """
        guild = ctx.guild
        f_word = word.lower()
        if f_word in await self.config.guild(guild).strict_filtered():
            async with self.config.guild(guild).strict_filtered() as less:
                less.remove(f_word)
            await ctx.send("Removed {} from the filter".format(word))
        else:
            async with self.config.guild(guild).strict_filtered() as more:
                more.append(f_word)
            await ctx.send("Added {} to the filter".format(word))

    @filter.command()
    async def whitelist(self, ctx, *, word: str):
        """
        This adds the word to a whitelist list
        """
        guild = ctx.guild
        except_word = word.lower()
        if except_word in await self.config.guild(guild).whitelist():
            async with self.config.guild(guild).whitelist() as move:
                move.remove(except_word)
            await ctx.send("Removed {} from the whitelist".format(word))
        else:
            async with self.config.guild(guild).whitelist() as move:
                move.append(except_word)
            await ctx.send("Added {} to the whitelist".format(word))

    @filter.command()
    async def channel(self, ctx, channel: discord.TextChannel, *, word: str):
        """
        testing
        """
        f_word = word.lower()
        if f_word in await self.config.channel(channel).filtered():
            async with self.config.channel(channel).filtered() as less:
                less.remove(f_word)
            await ctx.send("Removed {} from the filter".format(word))
        else:
            async with self.config.channel(channel).filtered() as more:
                more.append(f_word)
            await ctx.send("Added {} to the filter".format(word))

    @commands.Cog.listener()
    async def on_message(self, message):
        guild = message.guild
        author = message.author
        hit = None
        strict_hit = None
        white_hit = None

        if not message.guild:
            return False

        if await self.bot.is_automod_immune(message.author):
            return False

        filters = await self.config.guild(guild).filtered()  # Not strict
        log = await self.config.guild(guild).logs()
        strict = await self.config.guild(guild).strict_filtered()  # Strict
        whitelist = await self.config.guild(guild).whitelist()  # Whitelist
        if whitelist:
            white_check = re.compile("|".join(rf"{re.escape(w)}" for w in whitelist))
            if white_check is not None:  # Exception/Whitelist setup
                white_hit = white_check.findall(message.content.lower())
            else:
                white_hit = False
        if strict:  # Strict setup
            strict_check = re.compile("|".join(rf"\b{re.escape(w)}\b" for w in strict))
            if strict_check is not None:
                strict_hit = strict_check.findall(message.content.lower())
            else:
                strict_hit = False
        if filters:  # Non strict setup
            check = re.compile("|".join(rf"{re.escape(w)}" for w in filters))
            if check is not None:
                hit = check.findall(message.content.lower())
            else:
                hit = False
        if hit or strict_hit:  # If strict hits or if non-strict hits continue process
            if white_hit:  # If it hits a whitelisted word/sentence, nothing happens
                return False
            try:
                await message.delete()
            except discord.Forbidden:
                pass
            except discord.NotFound:
                pass
            if log is not None:
                embed = discord.Embed(
                    title=f"{author.name}#{author.discriminator} - Filtered Mesasge",
                    description=f"```{message.content}```",
                    color=discord.Colour.dark_red(),
                )
                embed.set_footer(text=f"User ID: {author.id}")
                try:
                    await self.bot.get_channel(log).send(embed=embed)
                except discord.Forbidden:
                    pass
                except discord.HTTPException:
                    embed = discord.Embed(
                        title=f"{author.name}#{author.discriminator} - Filtered Mesasge",
                        description=f"```Mesasge too large to fit in embed```",
                        color=discord.Colour.dark_red(),
                    )
                    embed.set_footer(text=f"User ID: {author.id}")
                    try:
                        await self.bot.get_channel(log).send(embed=embed)
                    except discord.Forbidden:
                        pass

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        await self.on_message(after)
