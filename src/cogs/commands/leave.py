from disnake.ext import commands


class TestLeave(commands.Cog):
    def __init__(self, bot):
        super(TestLeave, self).__init__()
        self.bot = bot

    @commands.command(name="leave")
    async def leave(self, ctx):
        leaves = list()
        for guild in self.bot.guilds:
            if guild.member_count < 10:
                leaves.append(guild.name)
                await guild.leave()
        await ctx.send(f"Покинул сервера: {', '.join([guild for guild in leaves])}")


def setup(bot: commands.Bot):
    bot.add_cog(TestLeave(bot))
