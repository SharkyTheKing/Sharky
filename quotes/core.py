import json
import random
from datetime import datetime
from io import BytesIO
from typing import Optional

import discord
from redbot.core import Config, checks, commands
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu, start_adding_reactions
from redbot.core.utils.predicates import ReactionPredicate

# TODO: Fix up export/import and history setup for more cohesive style
# TODO: Allow for customized quote message - Account for possible abuse
# TODO: Be able to search categories in quotesearch


class Quotes(commands.Cog):
    """
    Quote system for storing and retrieving memorable moments.
    """

    __author__ = ["SharkyIsAKing"]
    __version__ = "1.0.0"

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=4242424242)
        self.config.register_guild(quotes=[], last_quote=None, editlog=[])

    def format_help_for_context(self, ctx: commands.Context) -> str:
        context = super().format_help_for_context(ctx)
        authors = ", ".join(self.__author__)
        return f"{context}\n\nAuthor: {authors}\nVersion: {self.__version__}"

    async def yes_or_no(self, ctx, message) -> bool:
        msg = await ctx.send(message)
        start_adding_reactions(msg, ReactionPredicate.YES_OR_NO_EMOJIS)

        pred = ReactionPredicate.yes_or_no(msg, ctx.author)
        await ctx.bot.wait_for("reaction_add", check=pred)
        await msg.delete()
        return pred.result

    async def _get_quotes(self, guild):
        return await self.config.guild(guild).quotes()

    async def _set_quotes(self, guild, quotes):
        await self.config.guild(guild).quotes.set(quotes)

    @commands.guild_only()
    @commands.command()
    async def quotelist(self, ctx):
        """
        View all quotes that are stored from the server!
        """
        quotes = await self._get_quotes(ctx.guild)
        if not quotes:
            await ctx.send("❌ There are no quotes to list.")
            return

        pages = []
        per_page = 10  # limit how many per page

        for i in range(0, len(quotes), per_page):
            embed = discord.Embed(
                title=f"📚 Quote List (Page {i//per_page + 1}/{(len(quotes) - 1)//per_page + 1})",
                color=discord.Color.blue(),
            )
            chunk = quotes[i : i + per_page]

            for idx, q in enumerate(chunk, start=i + 1):
                timestamp = f"<t:{q.get('timestamp', 0)}:f>"
                category = f" | 🏷️ {q['category']}" if q.get("category") else ""
                added_by = q.get("added_by", "Unknown")
                embed.add_field(
                    name=f"📖 Quote #{idx}",
                    value=f"{q['quote']}\n➕ Added by **{added_by}** on {timestamp}{category}",
                    inline=False,
                )

            pages.append(embed)

        await menu(ctx, pages, controls=DEFAULT_CONTROLS, timeout=60.0)

    @commands.guild_only()
    @commands.command(usage="<text>")
    async def addquote(self, ctx, *, input_text: str):
        """
        Add a new quote. Optional: `|| category:yourtag` at the end.

        [p]addquote Sharky fell in the water, he's now an actual shark! \|| category:shark
        [p]addquote Do you know the muffin man? THE ONE WHO LIVES IN AVENGERS TOWER?
        [p]addquote I smell cookies...and no ones making any \|| category:cookies
        """
        if "|| category:" in input_text:
            quote_text, category = input_text.split("|| category:", 1)
            category = category.strip().lower()
        else:
            quote_text = input_text
            category = None

        quote_entry = {
            "quote": quote_text.strip(),
            "added_by": ctx.author.name,
            "user_id": ctx.author.id,
            "timestamp": int(datetime.now().timestamp()),
            "category": category,
        }

        quotes = await self._get_quotes(ctx.guild)
        quotes.append(quote_entry)
        await self._set_quotes(ctx.guild, quotes)

        cat_info = f" under category `{category}`" if category else ""
        await ctx.send(f"✅ Quote #{len(quotes)} added by {ctx.author.name}{cat_info}.")

    @commands.guild_only()
    @commands.command(usage="[Quote Num]")
    async def quote(self, ctx, number: Optional[int]):
        """Get a quote by number or random if no number is given."""
        quotes = await self._get_quotes(ctx.guild)
        if not quotes:
            await ctx.send("❌ There are no quotes yet.")
            return

        if number is None:
            # number = random.randint(1, len(quotes))
            last_id = await self.config.guild(ctx.guild).last_quote()
            indexes = list(range(len(quotes)))

            if last_id is not None and len(quotes) > 1:
                # Temporarily exclude the last used quote
                indexes.remove(last_id)

            selected_index = random.choice(indexes)
            # store so we prevent reuse
            await self.config.guild(ctx.guild).last_quote.set(selected_index)
        else:
            if number < 1 or number > len(quotes):
                await ctx.send(f"❌ There's no quote for number {number} yet.")
                return
            selected_index = number - 1  # Manual selection doesn't affect last used

        # q = quotes[number - 1]
        q = quotes[selected_index]
        q.get("added_by", "Unknown")
        timestamp = f"<t:{q['timestamp']}:f>"
        f" | 🏷️ {q['category']}" if q.get("category") else ""

        await ctx.send(
            f"{q['quote']}\n**Quote #{selected_index + 1}**",
            allowed_mentions=discord.AllowedMentions(users=False),
        )

        # Keeping this commented for now - Until I can add in ability to make custom messages
        # await ctx.send(
        #    f"📜 **Quote #{selected_index + 1}:** {q['quote']}\n➕ Added by {added_by} on {timestamp}{category}"
        # )

    @commands.guild_only()
    @commands.command(aliases=["searchquote"])
    async def quotesearch(self, ctx: commands.Context, *, keyword: str):
        """
        Search for quotes containing a specific keyword.
        """
        quotes = await self._get_quotes(ctx.guild)
        matches = [
            (i + 1, q) for i, q in enumerate(quotes) if keyword.lower() in q["quote"].lower()
        ]

        if not matches:
            await ctx.send(f"❌ No quotes found containing: `{keyword}`")
            return

        pages = []
        per_page = 10
        total_pages = (len(matches) - 1) // per_page + 1
        for i in range(0, len(matches), per_page):
            embed = discord.Embed(
                title=(f"🔍 Quote Search: {keyword} " f"(Page {i // per_page + 1}/{total_pages})"),
                description=f"Found {len(matches)} matching quote(s).",
                color=discord.Color.blue(),
            )

            chunk = matches[i : i + per_page]

            for idx, q in chunk:
                timestamp = f"<t:{q.get('timestamp', 0)}:f>"
                category = f" | 🏷️ {q['category']}" if q.get("category") else ""
                added_by = q.get("added_by", "Unknown")

                embed.add_field(
                    name=f"📖 Quote #{idx}",
                    value=(
                        f"{q['quote']}\n"
                        f"➕ Added by **{added_by}** on "
                        f"{timestamp}{category}"
                    ),
                    inline=False,
                )

            pages.append(embed)

        await menu(
            ctx,
            pages,
            controls=DEFAULT_CONTROLS,
            timeout=60.0,
        )

    @commands.guild_only()
    @checks.mod_or_permissions(manage_messages=True)
    @commands.command()
    async def editquote(self, ctx, number: int, *, newquote: str):
        """Edits a quote by number and requires confirmation."""
        quotes = await self._get_quotes(ctx.guild)
        if number < 1 or number > len(quotes):
            await ctx.send(f"❌ There's no quote for number {number}.")
            return

        old_quote = quotes[number - 1]["quote"]

        confirm_message = (
            f"❓ Are you sure you want to replace:\n"
            f"**Old Quote #{number}:** `{old_quote}`\n\n"
            f"With:\n"
            f"**New Quote:** `{newquote}`\n\n"
            f"✅ React with **Yes** to confirm, or ❌ to cancel."
        )

        if await self.yes_or_no(ctx, confirm_message):
            quotes[number - 1]["quote"] = newquote
            await self._set_quotes(ctx.guild, quotes)
            await ctx.send(f"✅ Successfully updated Quote #{number}.")
            edit_entry = {
                "quote_number": number,
                "old_quote": old_quote,
                "new_quote": newquote,
                "edited_by": ctx.author.name,
                "user_id": ctx.author.id,
                "timestamp": int(datetime.utcnow().timestamp()),
            }
            async with self.config.guild(ctx.guild).editlog() as editlog:
                editlog.append(edit_entry)
        else:
            await ctx.send("❌ Edit cancelled.")

    @commands.guild_only()
    @checks.mod_or_permissions(manage_messages=True)
    @commands.command(aliases=["delquote"])
    async def removequote(self, ctx, number: int):
        """Remove a quote by number and renumber the rest."""
        quotes = await self._get_quotes(ctx.guild)
        if number < 1 or number > len(quotes):
            await ctx.send(f"❌ There's no quote for number {number}.")
            return

        removed = quotes.pop(number - 1)
        await self._set_quotes(ctx.guild, quotes)
        await ctx.send(f"🗑️ Removed quote #{number}: \"{removed['quote']}\"")

    @commands.guild_only()
    @commands.group()
    async def setquotes(self, ctx: commands.Context):
        """
        Edit, remove, import, export or look at quote histories!
        """

    @checks.mod_or_permissions(manage_messages=True)
    @setquotes.command()
    async def quoteexport(self, ctx):
        """Export all quotes to a JSON file."""
        quotes = await self._get_quotes(ctx.guild)
        if not quotes:
            await ctx.send("❌ There are no quotes to export.")
            return

        buffer = BytesIO()
        buffer.write(json.dumps(quotes, indent=2).encode("utf-8"))
        buffer.seek(0)
        await ctx.send(
            "📤 Here's your exported quotes:",
            file=discord.File(fp=buffer, filename="quotes_export.json"),
        )

    @checks.mod_or_permissions(manage_messages=True)
    @setquotes.command()
    async def quoteimport(self, ctx):
        """Import quotes from a previously exported JSON file."""
        if not ctx.message.attachments:
            await ctx.send("❌ Please attach a JSON file to import.")
            return

        attachment = ctx.message.attachments[0]
        try:
            data = await attachment.read()
            imported = json.loads(data)
            if not isinstance(imported, list):
                raise ValueError("Not a list of quotes.")
        except Exception as e:
            await ctx.send(f"❌ Failed to read file: {e}")
            return

        await self._set_quotes(ctx.guild, imported)
        await ctx.send(f"✅ Successfully imported {len(imported)} quotes.")

    @checks.mod_or_permissions(manage_messages=True)
    @setquotes.command(name="quotehistory")
    async def quotehistory(self, ctx, user: discord.Member = None):
        """
        View paginated quote edit history.
        Optionally filter by user: `[p]quotehistory @user`
        """
        history = await self.config.guild(ctx.guild).editlog()

        if not history:
            return await ctx.send("No edits have been logged.")

        if user:
            history = [e for e in history if e["user_id"] == user.id]
            if not history:
                return await ctx.send(f"No edits found by {user.display_name}.")

        pages = []
        for entry in reversed(history):
            time = datetime.utcfromtimestamp(entry["timestamp"]).strftime("%Y-%m-%d %H:%M UTC")
            embed = discord.Embed(
                title=f"Quote #{entry['quote_number']} Edit", color=discord.Color.orange()
            )
            embed.add_field(name="Old", value=entry["old_quote"][:1024] or "None", inline=False)
            embed.add_field(name="New", value=entry["new_quote"][:1024] or "None", inline=False)
            embed.set_footer(text=f"Edited by {entry['edited_by']} • {time}")
            pages.append(embed)

        if not pages:
            return await ctx.send("No valid edits found.")

        # Send paginated message
        await menu(ctx, pages, controls=DEFAULT_CONTROLS, timeout=120)

    @checks.mod_or_permissions(manage_messages=True)
    @setquotes.command(name="exportlog")
    async def exportlog(self, ctx):
        """Export the full quote edit log as a JSON file."""
        history = await self.config.guild(ctx.guild).editlog()

        if not history:
            return await ctx.send("There is no edit log to export.")

        data = json.dumps(history, indent=2)
        buffer = BytesIO(data.encode("utf-8"))
        buffer.seek(0)

        filename = f"quote_editlog_{ctx.guild.id}.json"
        await ctx.send(
            content="Here is the export of the quote edit log.",
            file=discord.File(fp=buffer, filename=filename),
        )

    @checks.admin_or_permissions(administrator=True)
    @setquotes.command(name="clearlog")
    async def clearlog(self, ctx):
        """⚠️ Clear the entire quote edit log. This cannot be undone."""
        confirm = await self.yes_or_no(
            ctx,
            "⚠️ Are you sure you want to clear the entire quote edit log?\nThis action **cannot be undone**.\nReact with ✅ to confirm or ❌ to cancel.",
        )

        if not confirm:
            await ctx.send("❌ Log clear cancelled.")
            return

        await self.config.guild(ctx.guild).editlog.clear()
        await ctx.send("✅ Quote edit log has been cleared.")
