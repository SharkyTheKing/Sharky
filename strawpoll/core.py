import discord
import aiohttp
import asyncio

from redbot.core import commands, checks, Config
from redbot.core.utils.menus import start_adding_reactions
from redbot.core.utils.predicates import ReactionPredicate
from redbot.core.utils.predicates import MessagePredicate

#   Data example: data_info = {"poll": {"title": "Testing", "description": "This is a test", "answers": ["yes", "no", "maybe"], "priv": "true", "ma": 0,"mip" :0,"co": 1,"vpn": 0,"enter_name": 0,"has_deadline": "true","deadline": "2020-02-27T07:00:00.000Z","only_reg": 0,"has_image": 0,"image": "null"}}

#   data_info = {"poll":{"title":"Testing", "description":"This is a test", "answers":["yes", "no", "maybe"]}}
#   straw = requests.post("https://strawpoll.com/api/poll", data=data_info)


BaseCog = getattr(commands, "Cog", object)


class StrawPoll(BaseCog):
    """
    Making a strawpoll!
    """

    def __init__(self, bot):
        self.url = "https://strawpoll.com/api/poll"
        self.bot = bot
        self.one_person_check = {}
        self.session = aiohttp.ClientSession()

    def cog_unload(self):
        """
        Called when cog is unloaded or bot is restarted
        """
        self.bot.loop.create_task(self.session.close())

    async def yes_or_no(self, ctx, message) -> bool:
        msg = await ctx.send(message)
        start_adding_reactions(msg, ReactionPredicate.YES_OR_NO_EMOJIS)

        pred = ReactionPredicate.yes_or_no(msg, ctx.author)
        try:
            await ctx.bot.wait_for("reaction_add", check=pred, timeout=30)
        except asyncio.TimeoutError:
            await self.clearing_guild_cache(ctx.guild)
            return False
        await msg.delete()
        return pred.result

    async def get_title_info(self, ctx, message, json_info) -> bool:
        await ctx.send(message)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            title_message = await ctx.bot.wait_for("message", check=check, timeout=60)
            json_info["poll"]["title"] = title_message.content
        except asyncio.TimeoutError:
            await ctx.send("You took too long to reply...")
            await self.clearing_guild_cache(ctx.guild)
            return False
        return True

    async def get_description_info(self, ctx, message, json_info) -> bool:
        await ctx.send(message)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            description_message = await ctx.bot.wait_for("message", check=check, timeout=80)
            json_info["poll"]["description"] = description_message.content
        except asyncio.TimeoutError:
            await ctx.send("You took too long to reply...")
            return False

    async def get_multiple_choices(self, ctx, message, json_info) -> bool:
        await ctx.send(message)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            multiple_choies = await ctx.bot.wait_for("message", check=check, timeout=150)
            word_list = []
            tmp = ""
            splits = multiple_choies.content.split()
            for words in splits:
                if not words.startswith('"') and not words.endswith('"') and not tmp:
                    word_list.append(words)
                else:
                    if words.startswith('"'):
                        tmp += words[1:] + " "
                    elif words.endswith('"'):
                        tmp += words[:-1]
                        word_list.append(tmp)
                        tmp = ""
                    else:
                        tmp += words + " "
            json_info["poll"]["answers"] = word_list
            return True
        except asyncio.TimeoutError:
            return False

    @commands.command()
    async def strawpoll(self, ctx):
        """
        Create a new strawpoll!
        """
        try:
            if self.one_person_check[ctx.guild.id]:
                return await ctx.send(
                    "Currently in use. Please wait until the person has finished their poll"
                )
        except KeyError:
            pass

        self.one_person_check.update({ctx.guild.id: ctx.author.id})
        confirmation = await self.yes_or_no(ctx, "Do you want to create a new strawpoll? Yes/No")
        json_info = {
            "poll": {
                "title": None,
                "description": None,
                "answers": ["Yes.", "No", "Maybe"],
                "ma": False,
            }
        }
        if not confirmation:
            await ctx.send("You...why did you even use this command then?")
            await self.clearing_guild_cache(ctx.guild)
            return False

        title = await self.get_title_info(
            ctx=ctx,
            message="What title do you want? You got 60 seconds to reply.",
            json_info=json_info,
        )

        description = await self.get_description_info(
            ctx=ctx,
            message="What description do you want? You have 80 seconds to reply.",
            json_info=json_info,
        )
        confirm_choices = await self.yes_or_no(
            ctx, "Do you want to have custom choices? Default is `Yes, Maybe, No`"
        )

        if confirm_choices:
            answers = await self.get_multiple_choices(
                ctx,
                'Please type out your multiple answers.\nIf you are using more than one word for an answer, please put it in quotes. `"This is what I mean"`\nAn example: `Pizza Tacos "Mac and Cheese"`',
                json_info=json_info,
            )
            if not answers:
                await self.clearing_guild_cache(ctx.guild)
                return await ctx.send("Sorry, you didn't answer the answers in time.")

        confirm_multiple_answer = await self.yes_or_no(
            ctx,
            "Do you want to allow people to vote on more than one option? Default is set to only voting on one. Yes/No",
        )
        if confirm_multiple_answer:
            json_info["poll"]["ma"] = True

        if title is False or description is False:
            await self.clearing_guild_cache(ctx.guild)
            return await ctx.send("Canceled. You must have a title and a description")

        data = await self.getting_straw_data(ctx=ctx, json_info=json_info)
        if not data:
            return await ctx.send("Something happened... Couldn't get/send strawpoll information.")

        await ctx.send(data)

    async def getting_straw_data(self, ctx, json_info):
        try:
            async with self.session.post(self.url, json=json_info) as straw:
                if straw.status != 200:
                    return None
                end_url = await straw.json()
                message = "https://strawpoll.com/" + str(end_url["content_id"])
                await self.clearing_guild_cache(ctx.guild)
                return message
        except aiohttp.ClientConnectionError:
            return None

    async def clearing_guild_cache(self, guild: discord.Guild):
        """
        Does what it says, wipes the cache if anything fails
        """
        try:
            self.one_person_check.pop(guild.id)
        except KeyError:
            pass
        return self.one_person_check
