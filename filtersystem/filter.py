import discord
from redbot.core import commands, Config, checks
from redbot.core.utils.chat_formatting import box, pagify
from redbot.core.utils.menus import start_adding_reactions
from redbot.core.utils.predicates import ReactionPredicate

import re
from typing import Optional
from .auditlog import AuditLogging, PrivateLogEntry, PublicLogEntry

BaseCog = getattr(commands, "Cog", object)


class FilterSystem(BaseCog, AuditLogging):
    """
    Filter stuff here!

    You can only filter something one at a time, if you filter something, it'll take the whole filter into context...so don't filter the letter x
    This can't be used with the CORE filter system as this uses the commands based off of it.
    """

    def __init__(self, bot):
        self.bot = bot
        self.added_color = discord.Color.green()
        self.removed_color = discord.Color.dark_red()
        self.config = Config.get_conf(self, identifier=2398472689223426)
        def_guild = {
            "logs": None,
            "filtered": [],
            "strict_filtered": [],
            "whitelist": [],
            "private_logs": None,
        }
        # Filtered = Strict command. Strict_Filtered = Exact
        def_channel = {"filtered": [], "whitelist": []}
        self.config.register_guild(**def_guild)
        self.config.register_channel(**def_channel)
        # self.private_log = AuditLogging(self.config)

    async def yes_or_no(self, ctx, message) -> bool:
        msg = await ctx.send(message)
        start_adding_reactions(msg, ReactionPredicate.YES_OR_NO_EMOJIS)

        pred = ReactionPredicate.yes_or_no(msg, ctx.author)
        await ctx.bot.wait_for("reaction_add", check=pred)
        await msg.delete()
        return pred.result

    async def word_count_validation(self, ctx, word: str) -> bool:
        if len(word) <= 4:
            confirmation_message = await self.yes_or_no(
                ctx, f"{word} has 4 or less characters, are you sure you want to add?"
            )
            if not confirmation_message:
                await ctx.send(f"{word} won't be added.")
                return False

    async def truncate_message_content(self, message: discord.Message) -> str:
        if len(message.content.split()) > 25:
            return message.content[:120] + "... (shortened)"
        # probably a check here for total length too? I dno
        else:
            return message.content

    async def global_filter_check(self, ctx, word: str) -> bool:
        strict_filter = await self.config.guild(ctx.guild).filtered()
        exact_filter = await self.config.guild(ctx.guild).strict_filtered()
        whitelist = await self.config.guild(ctx.guild).whitelist()
        if word.lower() in strict_filter:
            await ctx.send("That word is already in the strict filter")
            return False
        elif word.lower() in exact_filter:
            await ctx.send("That word is already in the exact filter")
            return False
        elif word.lower() in whitelist:
            await ctx.send("That word is already in the whitelist")
            return False

    async def channel_filter_check(self, ctx, channel, word: str) -> bool:
        strict_filter = await self.config.channel(channel).filtered()
        whitelist = await self.config.channel(channel).whitelist()
        if word.lower() in strict_filter:
            await ctx.send(f"That word is already in {channel.mention}'s strict filter")
            return False
        elif word.lower() in whitelist:
            await ctx.send(f"That word is already in {channel.mention}'s whitelist")
            return False

    @staticmethod  # Thank you zixy
    def split_len(seq, length):
        """
        Splits a sequence into n sized pieces
        stolen from stacktrace
        """
        return [seq[i : i + length] for i in range(0, len(seq), length)]

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
    async def list(
        self, ctx, channel: Optional[discord.TextChannel], private_mesasge: bool = True
    ):
        """
        Gives you the entire list of filtered words

        If no channel is given, it'll default to guild. If a channel IS given, it'll show that channel's filters

        If you put `False` at the end, it'll send in the current channel.
        """
        guild = ctx.guild
        author = ctx.author
        target = author if private_mesasge else ctx.channel
        filter_list = ""
        whitelist_list = ""
        exact_list = ""
        filter_channel_amount = ""
        whitelist_channel_amount = ""
        #  Displays global filter
        if channel is None:
            #   Config setup
            filters = await self.config.guild(
                guild
            ).filtered()  # This is from the 'STRICT' command
            exact = await self.config.guild(
                guild
            ).strict_filtered()  # This is from the 'EXACT' command
            whitelist = await self.config.guild(guild).whitelist()
            #   Message setups

            channel_msg = ""  # Place holder for channel message
            if filters and exact and whitelist is None:
                return
            #   Filter info
            if filters:
                filter_list = ", ".join("'" + filters_count + "'" for filters_count in filters)
            #   Exact info
            if exact:
                exact_list = ", ".join("'" + exact_count + "'" for exact_count in exact)
            #   Whitelist Info
            if whitelist:
                whitelist_list = ", ".join("'" + white_count + "'" for white_count in whitelist)
            # Channel infos
            for channels in ctx.guild.channels:
                filter_channel = await self.config.channel(channels).filtered()
                whitelist_channel = await self.config.channel(channels).whitelist()
                if filter_channel:
                    filter_channel_amount += f"{channels.mention} "
                if whitelist_channel:
                    whitelist_channel_amount += f"{channels.mention} "
            if filter_channel_amount:
                channel_msg += f"Channel Filters:\n{filter_channel_amount}\n"
            if whitelist_channel_amount:
                channel_msg += f"Channel Whitelist:\n{whitelist_channel_amount}"
            #   Sending Message
            try:
                filter_messages = FilterSystem.split_len(filter_list, 1800)
                exact_messages = FilterSystem.split_len(exact_list, 1800)
                whitelist_messages = FilterSystem.split_len(whitelist_list, 1800)

                await target.send(
                    f"Strict Filter in this server:\n{box(filter_messages.pop(0) if len(filter_list) > 0 else 'No filters added')}"
                )
                for filters in filter_messages:
                    await target.send(box(filters))
                await target.send(
                    f"Exact Filtered in this server:\n{box(exact_messages.pop(0) if len(exact_list) > 0 else 'No exact filter added')}"
                )
                for exact in exact_messages:
                    await target.send(box(exact))
                await target.send(
                    f"Whitelisted in this server:\n{box(whitelist_messages.pop(0) if len(whitelist_list) > 0 else 'No whitelist added')}"
                )
                for white in whitelist_messages:  # Totally not racist
                    await target.send(box(white))
                for page in pagify(channel_msg, delims=[" ", "\n"], shorten_by=8):
                    await target.send(page)
            except discord.Forbidden:
                await ctx.send("I can't send direct message to you.")
        else:
            #  This sends the channel filter info
            channel_msg = ""
            #   Config setup
            filter_channel = await self.config.channel(channel).filtered()
            whitelist_channel = await self.config.channel(channel).whitelist()
            # Filter info
            if filter_channel:
                filter_list = ", ".join(filter_channel)
            # Whitelist info
            if whitelist_channel:
                whitelist_list = ", ".join(whitelist_channel)
            filter_messages = FilterSystem.split_len(filter_list, 1800)
            whitelist_messages = FilterSystem.split_len(whitelist_list, 1800)
            await target.send(
                f"Filtered in {channel.mention}:\n{box(filter_messages.pop(0) if len(filter_list) > 0 else 'No filters added')}"
            )
            for filters in filter_messages:
                await target.send(box(filters))
            await target.send(
                f"Whitelisted in {channel.mention}:\n{box(whitelist_messages.pop(0) if len(whitelist_list) > 0 else 'No whitelist added')}"
            )
            for white in whitelist_messages:
                await target.send(box(white))

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

    @filter.group(name="strict")
    async def global_strict(self, ctx):
        """
        Add/Remove a word to the filter system

        Usage: `[p]filter strict add Sharky` to add, `[p]filter strict remove Sharky` to remove.
        """
        pass

    @global_strict.command(name="add")
    async def strict_add(self, ctx, *, word: str):
        """
        Adds a word to the filter.

        Usage: `[p]filter strict add Sharks`, if it's in the filter. It'll alert you.
        """
        author, guild = ctx.author, ctx.guild
        filter_checks = await self.global_filter_check(ctx, word)
        if filter_checks is False:
            return

        validate = await self.word_count_validation(ctx, word)
        if validate is False:
            return False

        async with self.config.guild(guild).filtered() as more:
            more.append(word.lower())
        try:
            await ctx.send(f"Added {word} to the filter")
        except discord.HTTPException:
            await ctx.send("Added that word to the filter")
        private_log_entry = PrivateLogEntry(ctx, word, "Global filter added")
        await self.send_log(private_log_entry)

    @global_strict.command(name="remove", aliases=["delete", "del"])
    async def strict_remove(self, ctx, *, word: str):
        """
        Removes a word from the filter.

        Usage `[p]filter strict remove Sharks`, if it's not in the filter it'll alert you.
        """
        author, guild = ctx.author, ctx.guild
        if word.lower() not in await self.config.guild(guild).filtered():
            return await ctx.send("That word is not in the filter")

        async with self.config.guild(guild).filtered() as less:
            less.remove(word.lower())
        try:
            await ctx.send(f"Removed {word} from the filter")
        except discord.HTTPException:
            await ctx.send("Removed the word from the filter")
        log_entry = PrivateLogEntry(ctx, word, f"Global filter removed", is_removed=True)
        await self.send_log(log_entry)

    @filter.group(name="exact")
    async def global_exact(self, ctx):
        """
        Adds/Removes a word that is being watched for the EXACT copies

        Usage: `[p]filter exact add tacos` will add, `[p]filter exact remove tacos` will remove from the filter.
        """
        pass

    @global_exact.command(name="remove", aliases=["delete", "del"])
    async def exact_remove(self, ctx, *, word: str):
        """
        Removes the word from the EXACT Filter.

        Usage: `[p]filter exact remove toasts` If the word isn't in the filter, it'll alert you.
        """
        author, guild = ctx.author, ctx.guild
        if word.lower() not in await self.config.guild(guild).strict_filtered():
            return await ctx.send("That word is not in the filter")

        async with self.config.guild(guild).strict_filtered() as less:
            less.remove(word.lower())
        try:
            await ctx.send(f"Removed {word} from the filter")
        except discord.HTTPException:
            await ctx.send("Removed that word from the filter")
        log_entry = PrivateLogEntry(ctx, word, f"Global strict removed", is_removed=True)
        await self.send_log(log_entry)

    @global_exact.command(name="add")
    async def exact_add(self, ctx, *, word: str):
        """
        Adds the word to the EXACT Filter.

        This means the word has to be an EXACT COPY of what you put in the filter, to be removed.
        Usage: `[p]filter exact add tacos` If it's already in the filter, it'll alert you.
        """
        author, guild = ctx.author, ctx.guild
        filter_checks = await self.global_filter_check(ctx, word)
        if filter_checks is False:
            return

        validate = await self.word_count_validation(ctx, word)
        if validate is False:
            return False

        async with self.config.guild(guild).strict_filtered() as more:
            more.append(word.lower())
        try:
            await ctx.send(f"Added the {word} to the filter")
        except discord.HTTPException:
            await ctx.send("Added that word to the filter")
        log_entry = PrivateLogEntry(ctx, word, f"Global strict added")
        await self.send_log(log_entry)

    @filter.group(name="whitelist")
    async def global_whitelist(self, ctx):
        """
        Adds/Removes the word from the global whitelist

        Useful if you want to filter something, but also not have certain things removed
        """
        pass

    @global_whitelist.command(name="remove", aliases=["delete", "del"])
    async def whitelist_remove(self, ctx, *, word: str):
        """
        This removes a word from the whitelist

        Usage: `[p]filter whitelist remove twinkies`
        """
        author, guild = ctx.author, ctx.guild
        if word.lower() not in await self.config.guild(guild).whitelist():
            return await ctx.send("That word is not in the whitelist")

        async with self.config.guild(guild).whitelist() as move:
            move.remove(word.lower())
        try:
            await ctx.send(f"Removed {word} from the whitelist")
        except discord.HTTPException:
            await ctx.send("Removed that word from the whitelist")
        log_entry = PrivateLogEntry(ctx, word, f"Global whitelist removed", is_removed=True)
        await self.send_log(log_entry)

    @global_whitelist.command(name="add")
    async def whitelist_add(self, ctx, *, word: str):
        """
        This adds a word to the whitelist

        Usage: `[p]filter whitelist add fortnite`
        """
        author, guild = ctx.author, ctx.guild
        filter_checks = await self.global_filter_check(ctx, word)
        if filter_checks is False:
            return

        validate = await self.word_count_validation(ctx, word)
        if validate is False:
            return False

        async with self.config.guild(guild).whitelist() as move:
            move.append(word.lower())
        try:
            await ctx.send(f"Added {word} to the whitelist")
        except discord.HTTPException:
            await ctx.send("Added that word to the whitelist")
        log_entry = PrivateLogEntry(ctx, word, f"Global whitelist added")
        await self.send_log(log_entry)

    @filter.group()
    async def channel(self, ctx):
        """
        Filter system for channel specifics

        Add/Remove words to a channel filter (Usage: `[p]filter channel strict #general Looking for fun`)

        Add/Remove words to a channel whitelist (Usage: `[p]filter channel whitelist #general Looking for love`)
        """
        pass

    @channel.group(name="strict")
    async def channel_strict(self, ctx):
        """
        Add/remove a word to a channel filter

        Useful for when you want to filter something in a specific channel
        """
        pass

    @channel_strict.command(name="remove", aliases=["delete", "del"])
    async def channel_strict_remove(self, ctx, channel: discord.TextChannel, *, word: str):
        """
        Removes a word from a specific channel's filter

        Usage: `[p]filter channel strict remove #channel-name/channel-id soulrift`
        """
        if word.lower() not in await self.config.channel(channel).filtered():
            return await ctx.send("That word is not in the filter")

        async with self.config.channel(channel).filtered() as less:
            less.remove(word.lower())
        try:
            await ctx.send(f"Removed {word} from the filter")
        except discord.HTTPException:
            await ctx.send("Removed that word from the filter")
        log_entry = PrivateLogEntry(
            ctx, word, f"{channel} filter removed.", is_removed=True, channel=channel
        )
        await self.send_log(log_entry)

    @channel_strict.command(name="add")
    async def channel_strict_add(self, ctx, channel: discord.TextChannel, *, word: str):
        """
        Adds a word to a specific channel's filter

        Usage: `[p]filter channel strict add #channel-name/channel-id fishey`
        """
        filter_checks = await self.channel_filter_check(ctx, channel, word)
        if filter_checks is False:
            return

        validate = await self.word_count_validation(ctx, word)
        if validate is False:
            return False

        async with self.config.channel(channel).filtered() as more:
            more.append(word.lower())
        try:
            await ctx.send(f"Added {word} to the filter")
        except discord.HTTPException:
            await ctx.send("Added that word to the filter")
        log_entry = PrivateLogEntry(ctx, word, f"{channel} filter added.", channel=channel)
        await self.send_log(log_entry)

    @channel.group(name="whitelist")
    async def channel_whitelist(self, ctx):
        """
        Add/remove a word to a channel's whitelist

        This will make sure if a word matches any other filter, it won't be filtered regardless.
        """
        pass

    @channel_whitelist.command(name="remove", aliases=["delete", "del"])
    async def channel_whitelist_remove(self, ctx, channel: discord.TextChannel, *, word: str):
        """
        Removes a word from a channel's whitelist

        Usage: `[p]filter channel whitelist remove #channel-name/channel-id Ifoundcookies`
        """
        if word.lower() not in await self.config.channel(channel).whitelist():
            return await ctx.send("That word is not in the filter")

        async with self.config.channel(channel).whitelist() as less:
            less.remove(word.lower())
        try:
            await ctx.send(f"Removed {word} from the whitelist")
        except discord.HTTPException:
            await ctx.send("Removed that word from the whitelist")
        log_entry = PrivateLogEntry(
            ctx, word, f"{channel} whitelist removed.", is_removed=True, channel=channel
        )
        await self.send_log(log_entry)

    @channel_whitelist.command(name="add")
    async def channel_whitelist_add(self, ctx, channel: discord.TextChannel, *, word: str):
        """
        Adds a word to a channel's whitelist

        Usage: `[p]filter channel whitelist add #channel-name/channel-id heyisthatmycookie`
        """
        filter_checks = await self.channel_filter_check(ctx, channel, word)
        if filter_checks is False:
            return

        validate = await self.word_count_validation(ctx, word)
        if validate is False:
            return False

        async with self.config.channel(channel).whitelist() as more:
            more.append(word.lower())
        try:
            await ctx.send(f"Added {word} to the whitelist")
        except discord.HTTPException:
            await ctx.send("Added that word to the whitelist")
        log_entry = PrivateLogEntry(ctx, word, f"{channel} whitelist added.", channel=channel)
        await self.send_log(log_entry)

    @commands.command()
    @checks.admin_or_permissions(manage_guild=True)
    async def filterprivatelog(self, ctx, *, channel: Optional[discord.TextChannel]):
        """
        For admins of the server to see who filters what words/messages
        """
        guild = ctx.guild
        private_log_channel = self.config.guild(guild).private_logs
        if channel is None:
            await private_log_channel.clear()
            await ctx.send("Cleared the logging channel")
        else:
            await private_log_channel.set(channel.id)
            await ctx.send("Set the current logging channel to {}".format(channel.mention))

    @commands.Cog.listener(name="on_message_without_command")
    async def _listening_for_trouble(self, message):
        guild = message.guild
        channel = message.channel
        hit = None
        strict_hit = None  # Rename to exact
        white_hit = None
        channel_hit = None
        channel_white_hit = None

        if not message.guild:
            return False

        if isinstance(message.author, discord.Member):
            if await self.bot.is_automod_immune(message.author):
                return False

        chan_filter = await self.config.channel(channel).filtered()  # Channel Strict
        chan_whitelist = await self.config.channel(channel).whitelist()  # Channel Whitelist
        filters = await self.config.guild(guild).filtered()  # Strict
        strict = await self.config.guild(guild).strict_filtered()  # Exact
        whitelist = await self.config.guild(guild).whitelist()  # Whitelist
        filter_list = []
        if whitelist:
            white_check = re.compile("|".join(rf"{re.escape(w)}" for w in whitelist))
            if white_check is not None:  # Exception/Whitelist setup
                white_hit = white_check.findall(message.content.lower())
            else:
                white_hit = False
        if strict:  # Exact setup
            strict_check = re.compile("|".join(rf"\b{re.escape(w)}\b" for w in strict))
            if strict_check is not None:
                strict_hit = strict_check.findall(message.content.lower())
                filter_list.extend(strict_hit)
            else:
                strict_hit = False
        if filters:  # Non Exact setup
            check = re.compile("|".join(rf"{re.escape(w)}" for w in filters))
            if check is not None:
                hit = check.findall(message.content.lower())
                filter_list.extend(hit)
            else:
                hit = False
        #   Channel setups
        if chan_filter:  # Channel Strict
            chan_check = re.compile("|".join(rf"{re.escape(w)}" for w in chan_filter))
            if chan_check is not None:
                channel_hit = chan_check.findall(message.content.lower())
                filter_list.extend(channel_hit)
            else:
                channel_hit = False
        if chan_whitelist:  # Channel Whitelist
            chan_whitelist_check = re.compile("|".join(rf"{re.escape(w)}" for w in chan_whitelist))
            if chan_whitelist_check is not None:
                channel_white_hit = chan_whitelist_check.findall(message.content.lower())
            else:
                channel_white_hit = False

        if channel_hit or hit or strict_hit:
            if white_hit or channel_white_hit and not channel_hit:
                return False

            try:
                await message.delete()
            except (discord.errors.NotFound, discord.Forbidden, discord.HTTPException):
                pass

            log_entry = PublicLogEntry(message, filter_list)
            await self.send_log(log_entry)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        await self._listening_for_trouble(after)
