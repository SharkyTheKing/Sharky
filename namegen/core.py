import logging
from random import choice

import discord
from redbot.core import Config, checks, commands
from redbot.core.utils.chat_formatting import box

BASECOG = getattr(commands, "Cog", object)
DEF_GUILD = {"first_name": [], "last_name": [], "generated_message": None, "rename_members": False}


class NameGen(BASECOG):
    """
    Name Generator
    """

    def __init__(self, bot):
        self.bot = bot
        self.log = logging.getLogger("red.cogs.NameGen")
        self.default_message = "Your new name is:\n"

        self.config = Config.get_conf(self, identifier=740569763)
        self.config.register_guild(**DEF_GUILD)

    async def red_delete_data_for_user(self, **kwargs):
        """
        Nothing to delete
        """
        return

    @staticmethod  # Thank you zixy
    def split_len(seq, length):
        """
        Splits a sequence into n sized pieces
        stolen from stacktrace
        """
        return [seq[i : i + length] for i in range(0, len(seq), length)]

    @commands.group()
    @checks.mod_or_permissions(manage_nicknames=True)
    @commands.guild_only()
    async def nameset(self, ctx):
        """
        Adjust Name Generator settings
        """
        pass

    @nameset.command(name="list")
    async def showsettings(self, ctx):
        """
        Display name listing
        """
        last_name_list = ""
        first_name_list = ""

        first_name_config = await self.config.guild(ctx.guild).first_name()
        last_name_config = await self.config.guild(ctx.guild).last_name()
        gen_message = await self.config.guild(ctx.guild).generated_message()
        rename_or_message = await self.config.guild(ctx.guild).rename_members()

        if first_name_config:
            first_name_list = ", ".join(name_count for name_count in first_name_config)

        if last_name_config:
            last_name_list = ", ".join(name_count for name_count in last_name_config)

        first_name_message = NameGen.split_len(first_name_list, 1800)

        last_name_message = NameGen.split_len(last_name_list, 1800)

        await ctx.send(
            f"First names Stored:\n{box(first_name_message.pop(0)) if len(first_name_list) > 0 else 'No First Names'}"
        )

        await ctx.send(
            f"Last Names Stored:\n{box(last_name_message.pop(0)) if len(last_name_list) > 0 else 'No Last Names'}"
        )
        await ctx.send(
            f"Current settings: {'Will rename members' if rename_or_message else 'Will send message'}"
        )
        await ctx.send(f"Custom Message: {gen_message if gen_message else 'None Set'}")

    @nameset.command(name="rename")
    async def rename_or_message(self, ctx, toggle: bool):
        """
        Sets the cog to either renames or send message when command is used.

        Default settings are set to sending message. To change, type:
        `[p]nameset rename True`
        """
        if toggle is True:
            await self.config.guild(ctx.guild).rename_members.set(True)
            return await ctx.send("Done. Will now rename members.")
        elif toggle is False:
            await self.config.guild(ctx.guild).rename_members.set(False)
            return await ctx.send("Done. Will now send message.")

    @nameset.command(name="genmessage", aliases=["genmsg"])
    async def custom_generated_message(self, ctx, *, message: str):
        """
        Sets customized message when someone renames themselves.

        Put `None` to use default message.
        """
        if message.lower() == "none":
            await self.config.guild(ctx.guild).generated_message.set(None)
            return await ctx.send("Done. Set to default message")

        if len(message) > 1900:
            return await ctx.send("Error: Please use 1900 or less characters.")

        await self.config.guild(ctx.guild).generated_message.set(message)
        await ctx.send("Done! When someone renames themselves it'll say:\n{}".format(box(message)))

    @nameset.group(name="add")
    async def add_names(self, ctx):
        """
        Add names to list
        """
        pass

    @add_names.command(name="firstname", aliases=["first"])
    async def add_first_name(self, ctx, *names: str):
        """
        Add first names to the list
        """
        failed_to_add = ""
        for name in names:
            if name not in await self.config.guild(ctx.guild).first_name():
                async with self.config.guild(ctx.guild).first_name() as first_name:
                    first_name.append(name)
            else:
                failed_to_add += "{}\n".format(name)

        if not failed_to_add:
            message_to_send = "Done. Added your list of names to First Name"
        else:
            message_to_send = (
                "Done. Added your list of names to First Name"
                + "\nNames that were already in list: {}".format(failed_to_add)
            )
        await ctx.send(message_to_send)

    @add_names.command(name="lastname", aliases=["last"])
    async def add_last_name(self, ctx, *names: str):
        """
        Add last names to the list
        """
        failed_to_add = ""
        for name in names:
            if name not in await self.config.guild(ctx.guild).last_name():
                async with self.config.guild(ctx.guild).last_name() as last_name:
                    last_name.append(name)
            else:
                failed_to_add += "{}\n".format(name)

        if not failed_to_add:
            message_to_send = "Done. Added your list of names to Last Name"
        else:
            message_to_send = (
                "Done. Added your list of names to Last Name"
                + "\nNames that were already in list: {}".format(failed_to_add)
            )

        await ctx.send(message_to_send)

    @nameset.group(name="remove", aliases=["del", "rem"])
    async def remove_names(self, ctx):
        """
        Remove names from list
        """
        pass

    @remove_names.command(name="firstname", aliases=["first"])
    async def remove_first_name(self, ctx, *names: str):
        """
        Removes first name from the list
        """
        failed_to_remove = ""
        for name in names:
            if name in await self.config.guild(ctx.guild).first_name():
                async with self.config.guild(ctx.guild).first_name() as first_name:
                    first_name.remove(name)
            else:
                failed_to_remove += "{}\n".format(name)

        if not failed_to_remove:
            message_to_send = "Done. Removed your list of names from First Name"
        else:
            message_to_send = (
                "Done. Removed your list of names from First Name"
                + "\nNames that weren't already in list: {}".format(failed_to_remove)
            )

        await ctx.send(message_to_send)

    @remove_names.command(name="lastname", aliases=["last"])
    async def remove_last_name(self, ctx, *names: str):
        """
        Removes last name from the list
        """
        failed_to_remove = ""
        for name in names:
            if name in await self.config.guild(ctx.guild).last_name():
                async with self.config.guild(ctx.guild).last_name() as last_name:
                    last_name.remove(name)
            else:
                failed_to_remove += "{}\n".format(name)

        if not failed_to_remove:
            message_to_send = "Done. Removed your list of names from Last Name"
        else:
            message_to_send = (
                "Done. Removed your list of names from Last Name"
                + "\nNames that weren't already in list: {}".format(failed_to_remove)
            )

        await ctx.send(message_to_send)

    @commands.command(name="namegen")
    @commands.guild_only()
    async def generate_name(self, ctx):
        """
        Gives the person a new name
        """
        first_names = await self.config.guild(ctx.guild).first_name()
        last_names = await self.config.guild(ctx.guild).last_name()
        gen_message = await self.config.guild(ctx.guild).generated_message()
        rename = await self.config.guild(ctx.guild).rename_members()
        if not first_names:
            return await ctx.send("Nothing in First Names list")
        if not last_names:
            return await ctx.send("Nothing in Last Names list")

        generated_name = choice(first_names) + " " + choice(last_names)

        if rename:
            try:
                await ctx.author.edit(nick=generated_name, reason="Randomized name!")
            except discord.Forbidden:
                return await ctx.send("Sorry. We're unable to rename you.")

        if gen_message is None:
            message = self.default_message + generated_name
        else:
            message = gen_message + ":\n" + generated_name

        await ctx.send(message)
