from disnake import Intents, ApplicationCommandInteraction
from disnake.ext import commands
from os import listdir
from src.utils.utils import printc, determine_prefix


class BotClass(commands.Bot):
    def __init__(self):
        super(BotClass, self).__init__(command_prefix=determine_prefix, intents=Intents.all(), sync_commands_debug=True,
                                       help_command=None)

    # async def on_command_error(self, context: commands.Context, exception: Exception) -> None:
    #     printc("red", f"[ERROR]: {exception}")

    async def on_slash_command_error(
            self, interaction: ApplicationCommandInteraction, exception: Exception
    ) -> None:
        printc("red", f"[ERROR]: {exception}")

    async def on_message_command_error(
            self, interaction: ApplicationCommandInteraction, exception: Exception
    ) -> None:
        printc("red", f"[ERROR]: {exception}")

    async def on_user_command_error(
            self, interaction: ApplicationCommandInteraction, exception: Exception
    ) -> None:
        printc("red", f"[ERROR]: {exception}")

    async def on_connect(self):
        printc("yellow", "Connected to discord API. Loading sub-modules...")
        for dirs in listdir("src/cogs"):
            printc("yellow", f"Loading files from {dirs}...")
            self.load_extensions(f"src/cogs/{dirs}")
            printc("green", f"All files from {dirs} are loaded!")

    async def on_ready(self):
        printc("green", f"Logged to {self.user}")
