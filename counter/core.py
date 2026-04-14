import asyncio

import discord
from redbot.core import Config, bank, commands
from redbot.core.bot import Red


class Counter(commands.Cog):
    """
    A server-wide counting game with leaderboard, rewards, and a saves system.
    """

    __author__ = ["SharkyIsAKing"]
    __version__ = "1.0.0"

    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=89273589, force_registration=True)

        DEF_GUILD = {
            "count_channel": None,  # Where the counting happens
            "current_count": 0,  # incremental counter.
            "saves": 3,  # 3 saves originally until somoene buys or miscounts.
            "last_counter": None,  # user_id - Prevents same user from counting multiple times in a row.
            "save_price": 1000,  # default price for buysave
        }
        self.cache = {}
        self.config.register_guild(**DEF_GUILD)

    def format_help_for_context(self, ctx: commands.Context) -> str:
        context = super().format_help_for_context(ctx)
        authors = ", ".join(self.__author__)
        return f"{context}\n\nAuthor: {authors}\nVersion: {self.__version__}"

    def cog_unload(self):
        ...
        # .cancel()
        # When I work on cache system

    @commands.guild_only()
    @commands.group(name="counter")
    async def counting_set(self, ctx: commands.Context):
        """
        Counter game settings and buysave.

        Set the counting settings and buy saves for counting.
        """

    @commands.has_permissions(manage_messages=True)
    @counting_set.command(name="setchannel")
    async def setchannel(
        self, ctx: commands.Context, channel: discord.TextChannel = None
    ):  # change this to optional later
        """Set the channel where the counting takes place."""
        channel = channel if channel else None
        if not channel:
            await self.config.guild(ctx.guild).count_channel.set(None)
            return await ctx.send("Cleared the Counting Channel. Settings are saved.")

        await self.config.guild(ctx.guild).count_channel.set(channel.id)
        await ctx.send(
            f"📍 Counting channel has been set to {channel.mention}. If you want to reset the counter settings, please use `{ctx.prefix}counter resetguild`"
        )

    @commands.has_permissions(manage_messages=True)
    @counting_set.command(name="resetguild")
    async def reset_guild_stats(self, ctx: commands.Context):
        """Resets guild counter & stats."""
        await self.config.guild(ctx.guild).current_count.set(0)
        await self.config.guild(ctx.guild).saves.set(3)
        await self.config.guild(ctx.guild).last_counter.set(None)
        await ctx.send("✅ Guild settings (Current count, last counter, saves) have been reset.")

    @commands.has_permissions(manage_messages=True)
    @counting_set.command(name="setcount")
    async def set_the_counter(self, ctx: commands.Context, count: int):
        """Sets the current counter."""
        current_count = await self.config.guild(ctx.guild).current_count()
        await self.config.guild(ctx.guild).current_count.set(count)
        await ctx.send(
            f"🔢Counter has been changed to `{count}` the old count was {current_count}"
        )

    @commands.has_permissions(manage_messages=True)
    @counting_set.command(name="setprice")
    async def set_the_price(self, ctx: commands.Context, price: int):
        """
        Sets the price for the buysave.
        Please don't set this too high.
        """
        current_price = await self.config.guild(ctx.guild).save_price()
        await self.config.guild(ctx.guild).save_price.set(price)
        await ctx.send(
            f"💰BuySave Price has been changed to `{price}` the old price was {current_price}"
        )

    @commands.has_permissions(manage_messages=True)
    @counting_set.command(name="setsave")
    async def set_the_save(self, ctx: commands.Context, save: int):
        """
        Sets how many saves the server has."""
        if save <= 0:
            return await ctx.send(
                "❌ You cannot make saves 0 or less than 0. This will reset the game immediately upon failure."
            )
        current_save = await self.config.guild(ctx.guild).saves()
        await self.config.guild(ctx.guild).saves.set(save)
        await ctx.send(
            f"💾Saves has been changed to `{save}` the old save count was `{current_save}`"
        )

    @counting_set.command(name="status")
    async def status(self, ctx: commands.Context):
        """
        Checks current count, saves and possible future things.
        """
        data = await self.config.guild(ctx.guild).all()
        channel = ctx.guild.get_channel(data["count_channel"]) if data["count_channel"] else None
        embed = discord.Embed(title="🔢 Counting Status", color=discord.Color.green())

        embed.add_field(name="📊 Current Count", value=f"`{data['current_count']}`", inline=True)
        embed.add_field(name="💾 Saves Remaining", value=f"`{data['saves']}`", inline=True)
        embed.add_field(name="💰 BuySave Price", value=f"`{data['save_price']}`", inline=True)
        embed.add_field(
            name="📍 Counting Channel",
            value=channel.mention if channel else "Not Set",
            inline=False,
        )
        await ctx.send(embed=embed)

    @counting_set.command("buysave")
    async def buy_save(self, ctx: commands.Context):
        """Purchase an extra save for the counting game."""
        save_price = await self.config.guild(ctx.guild).save_price()
        user_balance = await bank.get_balance(ctx.author)

        if user_balance < save_price:
            await ctx.send(
                f"❌ You need {save_price} credits to buy a save, but you only have {user_balance}."
            )  # Figure out how to see if economy is loaded
            return

        await bank.withdraw_credits(ctx.author, save_price)
        current_saves = await self.config.guild(ctx.guild).saves()
        new_saves = current_saves + 1
        await self.config.guild(ctx.guild).saves.set(int(new_saves))

        await ctx.send(
            f"💾 You purchased a save for **{save_price}** credits! Total saves now: `{new_saves}`"
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.guild:
            return False

        if await self.bot.cog_disabled_in_guild(self, message.guild):
            return False

        if message.author.bot:
            return False

        if not message.content.isdigit():  # no point continuing if it's not a digit.
            return

        config_data = await self.config.guild(message.guild).all()
        # will eventually turn to cache

        if config_data["count_channel"] != message.channel.id:
            return  # prevents from doing further.

        expected = config_data["current_count"] + 1
        number = int(message.content)

        if number == expected:
            if config_data["last_counter"] == message.author.id:
                await message.channel.send(
                    f"⛔ You can't count twice in a row, {message.author.mention}!"
                )
                return

            await self.config.guild(message.guild).current_count.set(expected)
            await self.config.guild(message.guild).last_counter.set(message.author.id)

            await asyncio.sleep(
                1
            )  # I honestly forget why I had this here but I'm keeping it for now
            await message.add_reaction("✅")

        else:
            # Wrong number
            config_data["current_count"]
            saves = config_data["saves"]
            new_saves = saves - 1

            if saves > 0:
                await self.config.guild(message.guild).saves.set(new_saves)
                await message.channel.send(
                    f"⚠️ Wrong number! You used a save. Saves left: `{new_saves}`"
                )
            else:
                await self.config.guild(message.guild).current_count.set(0)
                await self.config.guild(message.guild).saves.set(3)
                await self.config.guild(message.guild).last_counter.set(None)
                await message.channel.send(
                    "❌ No saves left! The count resets to **1**, and saves have been restored to **3**."
                )
