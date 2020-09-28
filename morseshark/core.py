import discord
from redbot.core import commands, checks
import re

BASECOG = getattr(commands, "Cog", object)


class MorseShark(BASECOG):
    """
    In progress
    """

    def __init__(self, bot):
        self.bot = bot
        self.morse_code = {
            ".-": "a",
            "-...": "b",
            "-.-.": "c",
            "-..": "d",
            ".": "e",
            "..-.": "f",
            "--.": "g",
            "....": "h",
            "..": "i",
            ".---": "j",
            "-.-": "k",
            ".-..": "l",
            "--": "m",
            "-.": "n",
            "---": "o",
            ".--.": "p",
            "--.-": "q",
            ".-.": "r",
            "...": "s",
            "-": "t",
            "..-": "u",
            "...-": "v",
            ".--": "w",
            "-..-": "x",
            "-.--": "y",
            "--..": "z",
            ".----": "1",
            "..---": "2",
            "...--": "3",
            "....-": "4",
            ".....": "5",
            "-....": "6",
            "--...": "7",
            "---..": "8",
            "----.": "9",
            "-----": "0",
        }
        self.character_check = re.compile(r"(?i)[a-z0-9]+")
        self.morse_check = re.compile(r"(?i)[-.\\]+")

    @staticmethod
    def split(message):
        return [char for char in message]

    def decode_morse(self, message: str):
        word_list = []
        string = message.strip("!@#$%^&*()_+<>?,").split()
        for s in string:
            if s in self.morse_code:
                word_list.append(self.morse_code[s])
            if s == "/":
                word_list.append(" ")
        word_string = "".join(word_list)
        return word_string

    def encode_morse(self, message: str):
        alpha_code = {}
        alpha_code = {v: k for k, v in self.morse_code.items()}
        word_list = ""
        string = self.split(message.lower().strip("!@#$%^&*()_+<>?/,"))
        for s in string:
            if s in alpha_code:
                word_list += "{} ".format(alpha_code[s])
            if s == " ":
                word_list += "/ "
        return word_list

    @commands.group()
    async def morse(self, ctx):
        """
        Decode or Encode Morse code!

        Purely for fun
        """

    @morse.command()
    async def decode(self, ctx, *, message: str):
        confirm_decode = self.morse_check.match(message)
        if confirm_decode is None:
            return await ctx.send(
                "You must provide only morse characters. `-` or `.`, "
                "the only exception is `/` to explain where each words are."
            )
        decoded = self.decode_morse(message)
        await ctx.send(decoded)

    @morse.command()
    async def encode(self, ctx, *, message: str):
        confirm_letters = self.character_check.match(message)
        if not confirm_letters:
            return await ctx.send("You must provide only alphanumeric characters / numbers.")

        encoded = self.encode_morse(message)
        if not encoded:
            return await ctx.send("Something happened. Please try again.")
        await ctx.send(encoded)
