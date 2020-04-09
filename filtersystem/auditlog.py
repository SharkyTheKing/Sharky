from typing import Union

import discord
import logging
from redbot.core.commands.context import Context

from dataclasses import dataclass, field

log = logging.getLogger(name="red.filtersystem")


@dataclass()
class PrivateLogEntry:
    ctx: Context
    word: str
    title: str
    is_removed: bool = False
    channel: discord.TextChannel = None


@dataclass()
class PublicLogEntry:
    message: discord.Message
    hits: list
    author: discord.Member = field(init=False)
    channel: discord.TextChannel = field(init=False)

    def __post_init__(self):
        self.author = self.message.author
        self.channel = self.message.channel


class AuditLogging:
    # def __init__(self, config):
    #     self.config = config

    async def get_private_log_channel(self, guild: discord.Guild) -> discord.TextChannel:
        private_log_channel = await self.config.guild(guild).private_logs()
        return self.bot.get_channel(private_log_channel)

    async def get_public_log_channel(self, guild: discord.Guild) -> discord.TextChannel:
        public_log_channel = await self.config.guild(guild).logs()
        return self.bot.get_channel(public_log_channel)

    @staticmethod
    async def get_private_log_embed(entry: PrivateLogEntry) -> discord.Embed:
        embed = discord.Embed(
            title=entry.title,
            color=discord.Color.red() if entry.is_removed else discord.Color.green(),
        )
        embed.add_field(name="Word adjusted", value=f"```{entry.word}```")
        embed.add_field(
            name="Author", value=f"{entry.ctx.author} - `({entry.ctx.author.id})`", inline=False
        )

        embed.timestamp = entry.ctx.message.created_at
        return embed

    @staticmethod
    async def get_public_log_embed(entry: PublicLogEntry) -> discord.Embed:
        # gold to keep in touch with other automod actions
        embed = discord.Embed(title=f"Filtered message", color=discord.Color.gold())
        embed.set_author(name=f"{entry.author} - {entry.author.id}")
        embed.set_thumbnail(url=entry.author.avatar_url)
        embed.add_field(
            name="Message content", value=f"```{entry.message.content}```", inline=False
        )
        embed.add_field(name="Filtered from", value=entry.message.channel.mention)
        embed.add_field(
            name=f"Filter Hit{'s' if len(entry.hits) > 1 else ''}:",
            value=", ".join("`{0}`".format(w) for w in entry.hits),
        )

        embed.set_footer(text=f"User ID: {entry.author.id}")
        embed.timestamp = entry.message.created_at

        return embed

    async def send_log(self, entry: Union[PublicLogEntry, PrivateLogEntry]):
        if isinstance(entry, PublicLogEntry):
            embed = await self.get_public_log_embed(entry)
            log_channel = await self.get_public_log_channel(entry.message.guild)
        else:
            embed = await self.get_private_log_embed(entry)
            log_channel = await self.get_private_log_channel(entry.ctx.guild)

        if not log_channel:
            return False

        try:
            await log_channel.send(embed=embed)
        except discord.errors.Forbidden:
            log.warning(
                f"Missing permissions to send {entry.__class__.__name__} to channel {log_channel.id}"
            )
        except discord.errors.HTTPException as e:
            log.warning(f"Failed to send {entry.__class__.__name__}, {e.code} - {e.status}")
