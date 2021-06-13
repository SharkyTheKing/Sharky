import re

import discord
from redbot.core import checks, commands
from redbot.core.utils.chat_formatting import pagify

BASECOG = getattr(commands, "Cog", object)


class MorseShark(BASECOG):
    """
    Encoder/Decoder for morse codes!

    You can decode morse code into text or encode text into morse code.

    This was a simple cog to make, so if you want to take from this for your own, feel free.
    """

    __author__ = ["SharkyTheKing"]
    __version__ = "1.0.0"

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
            "--..--": ",",
            "..--..": "?",
            "-.-.--": "!",
            "---...": ":",
            ".-..-.": '"',
            ".----.": "`",
            "-...-": "=",
            "-.--.": "(",
            "-.--.-": ")",
            ".-...": "&",
            "-.-.-.": ";",
            ".-.-.": "+",
            "..--.-": "_",
            "...-..-": "$",
            ".--.-.": "@",
        }
        # need to double check ".----.": "`",in the future
        self.character_check = re.compile(r"(?i)[a-z0-9@$_+;&)(+`\":!\?,]+")
        self.morse_check = re.compile(r"(?i)[-.\\]+")

    async def red_delete_data_for_user(self, **kwargs):
        """
        Nothing to delete
        """
        return

    def format_help_for_context(self, ctx: commands.Context) -> str:
        context = super().format_help_for_context(ctx)
        authors = ", ".join(self.__author__)
        return f"{context}\n\nAuthor: {authors}\nVersion: {self.__version__}"

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
        string = self.split(message.lower().strip("#%^*<>/,"))
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

        If you would like to help add support for different characters/morse codes. Please contact me through the [Cog Support](https://discord.gg/GET4DVk) server. I'm happy to work with you to add more features.
        """
        pass

    @morse.command()
    async def decode(self, ctx, *, message: str):
        """
        Decode morse code into text!

        You must provide only morse characters. `-` or `.` The only exception is `/` to explain where each words are.

        Example: `[p]morse decode .. / .- -- / ... .... .- .-. -.- -.-- -.-.--`
        """
        confirm_decode = self.morse_check.match(message)
        if confirm_decode is None:
            return await ctx.send(
                "You must provide only morse characters. `-` or `.`, "
                "the only exception is `/` to explain where each words are."
            )
        decoded = self.decode_morse(message)
        if not decoded:
            return await ctx.send(
                "Sorry. I was unable to decode the morse code string.\n"
                "If this is a recurring issue, please contact Sharky through red's cog support server."
            )
        for page in pagify(decoded):
            await ctx.send(page)

    @morse.command()
    async def encode(self, ctx, *, message: str):
        """
        Encode text into morse code!

        You must provide alphanumeric characters/numbers only.
        """
        confirm_letters = self.character_check.match(message)
        if not confirm_letters:
            return await ctx.send("You must provide only alphanumeric characters / numbers.")

        encoded = self.encode_morse(message)
        if not encoded:
            return await ctx.send(
                "Was unable to encode your text into morse code."
                "\nIf this is a recurring issue, please reach out to my support channel."
                " Which is in red's cog support server."
            )
        for page in pagify(encoded):
            await ctx.send(page)
