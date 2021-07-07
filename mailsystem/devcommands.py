import asyncio
import io
from typing import Optional

import discord
from redbot.core import checks, commands
from redbot.core.utils.chat_formatting import box, humanize_list, pagify

from .embedmodel import EmbedSettings
from .mixins import MailSystemMixin


class DevCommands(MailSystemMixin):
    """
    Dev Commands for bot owner
    """

    @commands.group(name="mailset")
    async def mailsystem_settings(self, ctx: commands.Context):
        pass

    @checks.is_owner()
    @mailsystem_settings.group(name="dev")
    async def developer_commands(self, ctx: commands.Context):
        """
        Dev commands for Mailset
        """
        pass

    @developer_commands.command()
    async def activemail(self, ctx: commands.Context):
        """
        Previews how active mailsystem servers.
        """
        guild_list = []
        all_config = await self.config.all_guilds()
        for guild_id in all_config:
            if all_config[guild_id]["activation"]:
                guild_obj = ctx.bot.get_guild(guild_id)
                if not guild_obj:
                    try:
                        guild_obj = await ctx.bot.fetch_guild(guild_id)
                    except discord.HTTPException:
                        continue
                guild_list.append(guild_obj)

        msg = ""

        counter = 1
        for entry in guild_list:
            msg += f"[{counter}]:   {entry.name} - {entry.id}\n"

        message = "Active guilds: " + box(msg, lang="md")
        for page in pagify(message):
            await ctx.send(page)

    @developer_commands.command(name="guildconfig")
    async def check_guild_config(self, ctx: commands.Context, guild: discord.Guild):
        """
        Checks config for given guild for help.

        Allows you to check the settings per guild to help verify everything is set properly.
        """
        guild_config = await self.config.guild(guild).all()
        embed = await EmbedSettings.embed_list_setting(self, ctx, guild_config, guild)

        await ctx.send(embed=embed)

    @developer_commands.command(name="version")
    async def current_cog_version(self, ctx: commands.Context):
        """
        Displays current version.
        """
        await ctx.send("The current version is: `{version}`".format(version=self.__version__))

    @developer_commands.command()
    async def blockguild(self, ctx: commands.Context, guild: discord.Guild):
        """
        Blocks guilds from setting up mailsystem.

        This will completely wipe the guild's config and block them from setting up mailsystem.

        **Arguments:**
        - ``<guild>``: The guild you're wanting to block.
        """
        if guild.id in await self.config.ignore_guilds():
            return await ctx.send("Error. Guild already in block list.")

        await ctx.send(
            "Are you sure you want to block {guild} ({guild_id})".format(
                guild=guild.name, guild_id=guild.id
            )
        )

        confirmation_message = await self._return_yes_or_no(ctx)
        if not confirmation_message:
            return

        await self.config.guild(guild).clear()
        async with self.config.ignore_guilds() as block_guild:
            block_guild.append(guild.id)
        await ctx.send(
            "Successfully wiped {guild} ({guild_id})'s config and blocked it from setting up mailsystem.".format(
                guild=guild.name, guild_id=guild.id
            )
        )

    @developer_commands.command()
    async def unblockguild(self, ctx: commands.Context, guild: discord.Guild):
        """
        Unblocks a guild from setting up mailsystem.

        This will unblock the guild and allow them to set up mailsystem again.

        **Arguments:**
        - ``<guild>``: The guild you're wanting to unblock.
        """
        if guild.id not in await self.config.ignore_guilds():
            return await ctx.send("Error. Guild wasn't in the list.")

        async with self.config.ignore_guilds() as unblock_guild:
            unblock_guild.remove(guild.id)
        await ctx.send(
            "Successfully unblocked {guild} ({guild_id}). They can now setup mailsystem again.".format(
                guild=guild.name, guild_id=guild.id
            )
        )

    @developer_commands.command()
    async def listguildblock(self, ctx: commands.Context):
        """
        Lists all the guilds that are blocked.

        Will list every guild that is currently blocked from setting up mailsystem.
        """
        message = ", ".join(str(ctx.bot.get_guild(w)) for w in await self.config.ignore_guilds())
        if not message:
            return await ctx.send("There are no blocked guilds.")

        for page in pagify(message):
            await ctx.send(box(page))

    @mailsystem_settings.command(name="warn")
    async def warn_message_for_owner(self, ctx: commands.Context):
        """
        Displays this cog's current warn message.
        """
        warn_message = "**Warning: This Cog is still in testing, by installing and USING this Cog, you understand it comes with risks.**\n\nThis pre-release is to gather information, feedback, and issues from the community to improve the code. If you feel uncomfortable using this cog in its current state, uninstall it now.\n\nIf you have feedback or have an issue (bugs, breakage, bot blocking, etc) please send them to the proper place."
        embed = discord.Embed(
            title="MailSystem Warning", color=discord.Color.random(), description=warn_message
        )
        embed.add_field(name="Current version:", value=self.__version__)
        embed.add_field(name="Authors:", value=humanize_list(self.__author__))
        embed.add_field(
            name="Repo:", value="[Sharky's Cogs](https://github.com/SharkyTheKing/Sharky)"
        )
        await ctx.send(embed=embed)

    @checks.is_owner()
    @commands.command()
    async def testhtml(self, ctx):
        """
        Test
        """
        command_file = io.BytesIO()
        channel = ctx.bot.get_channel(853775084346540032)

        written_content = "<!DOCTYPE html>\n"

        written_content += "<body style='background-color:#36393f'>\n"
        written_content += "<style>\n.clipped {\n\tclip-path: circle();\n\n}\n</style>\n"
        written_content += "<style>\n.wrapwords {\n\tword-wrap: break-word;\ncolor:#bcddbf;\nfont-family: 'verdana'\n}\n</style>"
        written_content += (
            "<style>\n.authorname {\n\tcolor: white; font-family: 'verdana'\n}\n</style>\n"
        )
        written_content += "<style>\n.resizable {\n\tdisplay: inline-block;\n\tbackground: red;\n\tresize: both;\n\toverflow: hidden;\n\tline-height: 0;\n\twidth: 300px;\n\theight: auto;\n}\n"
        written_content += ".resizable img {\n\twidth: 100%;\n\theight: 100%;\n}\n</style>\n"

        async for m in channel.history(limit=5000, oldest_first=True):
            if m.embeds:
                written_content += "\n<img style='display:inline' src={avatar} width='30' height='30' class='clipped'/> <div style='display:inline' class='authorname'>{author_name}</div>\n".format(
                    avatar=m.embeds[0].author.icon_url, author_name=m.embeds[0].author.name
                )
                written_content += "<p class=wrapwords>{content}</p>".format(
                    content=m.embeds[0].description
                )
            else:
                if m.attachments:
                    written_content += "<br><div class='resizable'>"
                    written_content += "<img src='{attachment}' alt='Test' width='30' height='30'>\n</div></br>\n".format(
                        attachment=m.attachments[0].url
                    )
                    confirm_options = True
        written_content += "</body>"
        await ctx.send(len(written_content.encode()))
        command_file.write(written_content.encode())
        command_file.seek(0)
        await ctx.send(
            file=discord.File(command_file, filename="{}.html".format(ctx.channel.name))
        )
