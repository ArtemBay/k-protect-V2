import asyncio
import datetime
import json
import time

import src.utils.cache
import disnake
import src.messages
import src.word
from disnake.ext import commands

from config import Color, Other

cooldown_dict = {}


async def reset(id, delay):
    global cooldown_dict
    await asyncio.sleep(delay)
    try:
        del cooldown_dict[id]
    except (KeyError, Exception, BaseException):
        pass


class Dropdown(disnake.ui.View):
    def __init__(self, author, ctx):
        super().__init__()
        self.author = author
        infoe = disnake.Embed(color=Color.primary, title="ℹ | Список команд: Информация", description=f"""
        `{ctx}info` – информация о боте
        `{ctx}invite` – пригласить бота на свой сервер
        `{ctx}ping` – пинг бота
        `{ctx}server` – информация о сервере
        `{ctx}user` – информация о пользователе
                    """)
        modere = disnake.Embed(color=Color.primary, title="👮‍♂️ | Список команд: Модерация", description=f"""
        `{ctx}addroles` – выдать всем роль
        `{ctx}ban` – забанить пользователя
        `{ctx}bans` – список действующих банов
        `{ctx}correct` – исправить никнейм указанным участникам
        `{ctx}correct-all` – исправить никнейм всем участникам
        `{ctx}kick` – кикнуть участника
        `{ctx}lock-bot` – заблокировать бота
        `{ctx}mute` – замьютить участника
        `{ctx}mutes` – список действующих мьютов
        ~~`{ctx}purge` – очистить чат~~ (закрыто на обновление)
        `{ctx}quarantine` – управление карантином
        `{ctx}remroles` – забрать роль у всех участников
        `{ctx}unban` – разбанить пользователя
        `{ctx}unlock-bot` – разблокировать бота
        `{ctx}unmute` – размьютить участника
        `{ctx}unwarn` – снять предупреждение у участника
        `{ctx}warn` – выдать предупреждение участнику
        `{ctx}warns` – посмотреть свои или чужие предупреждения
                    """)
        admine = disnake.Embed(color=Color.primary, title="🛠 | Список команд: Администрация", description=f"""
        `{ctx}delspamchannels` – удалить каналы с одинаковым названием
        `{ctx}delspamroles` – удалить роли с одинаковым названием
        `{ctx}echo` – сказать что-нибудь от лица бота
        `{ctx}lock` – заблокировать канал
        `{ctx}massban` – забанить сразу несколько пользователей
        `{ctx}unlock` – разблокировать канал
                    """)
        fune = disnake.Embed(color=Color.primary, title="😂 | Список команд: Веселья", description=f"""
        `{ctx}8ball` – задать вопрос магическому шару
                    """)
        ownere = disnake.Embed(color=Color.primary, title="👑 | Список команд: Для владельца сервера",
                               description=f"""
        `{ctx}alertcrash` – снять всех администраторов и модераторов
        `{ctx}reset-all` – сбросить **все** настройки бота
                    """)
        settingse = disnake.Embed(color=Color.primary, title="⚙ | Список команд: Настройка", description=f"""
        `{ctx}antiraid` – настройка анти-рейда
        ~~`{ctx}antiflood` – настройка анти-флуда~~
        `{ctx}antiinvite` – настройка анти-приглашений
        `{ctx}muterole` – указать роль мьюта
        `{ctx}nickcorrector` – корректор никнеймов
        `{ctx}notify-dm` – оповещения о наказаниях в личку
        `{ctx}np` – наказание за краш
        `{ctx}nuker` – наказание за приглашение краш-бота
        `{ctx}perms` – ограничить команду по каналам и ролям
        `{ctx}prefix` – изменить префикс бота
        `{ctx}role-protect` – защита роли участника от изменения прав
        `{ctx}score` – управление баллами за краш
        `{ctx}warn-actions` – наказания за предупреждения
        `{ctx}whitelist` – белый список
                    """)
        rre = disnake.Embed(color=Color.primary, title="🎩 | Список команд: Роли за реакции", description=f"""
        `{ctx}addsingle` – добавить роль за реакцию
        `{ctx}delsingle` – удалить роль за реакцию
                    """)
        othere = disnake.Embed(color=Color.primary, title="💾 | Список команд: Прочее", description=f"""
        `{ctx}avatar` – получить аватар пользователя
        `{ctx}backup` – управление резервными копиями сервера
        `{ctx}discrim` – поиск участников с определённым disnake тегом
                    """)
        cpplus = disnake.Embed(color=Color.primary,
                               title="⭐ | Список команд: Управление подпиской CrashProtect Plus", description=f"""
        `{ctx}invoices` – выставленные счета
        `{ctx}plus` – подробнее о подписке
                    """)
        self.embeds = {
            "Информация": infoe,
            "Модерация": modere,
            "Веселья": fune,
            "Для владельца сервера": ownere,
            "Настройка": settingse,
            "Прочее": othere,
            "Роли за реакции": rre,
            "Администрация": admine,
            "CP Plus": cpplus
        }

    @disnake.ui.select(placeholder="Выберите категорию",
                       min_values=1,
                       max_values=1,
                       options=[
                           disnake.SelectOption(label="Информация", description="Информационные команды", emoji="ℹ"),
                           disnake.SelectOption(label="Модерация", description="Команды модерации", emoji="👮‍♂️"),
                           disnake.SelectOption(label="Администрация", description="Команды администраторов",
                                                emoji="🛠"),
                           disnake.SelectOption(label="Веселья", description="Команды для веселья", emoji="😃"),
                           disnake.SelectOption(label="Для владельца сервера",
                                                description="Команды, доступные только владельцу сервера", emoji="👑"),
                           disnake.SelectOption(label="Настройка", description="Команды для настройки бота", emoji="⚙"),
                           disnake.SelectOption(label="Роли за реакции", description="Команды для ролей за реакции",
                                                emoji="🎩"),
                           disnake.SelectOption(label="Прочее", description="Прочие команды", emoji="💾"),
                           disnake.SelectOption(label="CP Plus", description="Управление подпиской CrashProtect Plus",
                                                emoji="⭐"),
                       ])
    async def callback(self, _, interaction: disnake.MessageInteraction):
        if self.author == interaction.author:
            await interaction.send(embed=self.embeds[interaction.values[0]], ephemeral=True)
        else:
            await interaction.send("Доступ запрещён", ephemeral=True)


# async def callback(self, interaction: disnake.MessageInteraction):
#     pass


# class DropdownView(disnake.ui.View):
#     def __init__(self, author):
#         super().__init__()
#
#         self.add_item(Dropdown(author=author))


class Cmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="help", description="Помощь")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.check(src.messages.check_perms)
    async def help(self, interaction: disnake.UserCommandInteraction, category=None):
        if category is None:
            embed = disnake.Embed(
                title="💥 | Список команд",
                description=f"`<обязательный параметр>` `[необязательный параметр]`\n**Не используйте скобочки при "
                            f"указании параметров**\n\nИспользуйте `/help [команда]` для получения "
                            f"подробной информации о команде",
                color=Color.primary
            )
            embed.add_field(
                name=f"📘 | Инфо",
                value="`info` `invite` `ping` `server` `user`",
                inline=False
            )
            embed.add_field(
                name=f"⚒ | Модерация",
                value="`addroles` `ban` `bans` `correct` `correct-all` `kick` `lock-bot` `mute` `mutes` ~~`purge`~~ "
                      "`quarantine` `remroles` `unban` `unlock-bot` `unmute` `unwarn` `warn` `warns`",
                inline=False
            )
            embed.add_field(
                name=f"👑 | Администрация",
                value="`delspamchannels` `delspamroles` `echo` `lock` `massban` `unlock`",
                inline=False
            )
            embed.add_field(
                name=f"😂 | Веселья",
                value="`8ball`",
                inline=False
            )
            embed.add_field(
                name=f"🔥 | Для владельца сервера",
                value="`alertcrash` `reset-all`",
                inline=False
            )
            embed.add_field(
                name=f"⚙ | Настройка",
                value="`antiraid` ~~`antiflood`~~ `antiinvite` `muterole` `nickcorrector` `notify-dm` `np` `nuker` "
                      "`perms` `prefix` `role-protect` `score` `warn-actions` `whitelist`",
                inline=False
            )
            embed.add_field(
                name=f"🎩 | Роли за реакции",
                value="`addsingle` `delsingle`",
                inline=False
            )
            embed.add_field(
                name=f"🎲 | Прочее",
                value="`avatar` `backup` `discrim`",
                inline=False
            )
            embed.add_field(
                name=f"⭐ | CP Plus",
                value="`invoices` `plus`",
                inline=False
            )
            view = Dropdown(author=interaction.author, ctx="/")
            await interaction.send(embed=embed, view=view)

            # for i in range(20):
            #     inter = await self.bot.wait_for("dropdown", check=lambda
            #         inter: inter.message.id == msg.id and ctx.author == inter.author, timeout=300)
            #     embeds = {
            #         "Информация": infoe,
            #         "Модерация": modere,
            #         "Веселья": fune,
            #         "Для владельца сервера": ownere,
            #         "Настройка": settingse,
            #         "Прочее": othere,
            #         "Роли за реакции": rre,
            #         "Администрация": admine,
            #         "CP Plus": cpplus
            #     }
            #     await msg.edit(embed=embeds[inter.values[0]], view=view)
        else:
            cmd = src.messages.get_command(self.bot, category)
            if not cmd:
                return await interaction.send("Мы обыскали всё вдоль и поперёк, но так и не смогли найти эту команду.",
                                              ephemeral=True)
            with open("json/commandinfo.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            if cmd not in data:
                return await interaction.send(
                    "Об этой команде совсем ничего не известно, так как мой ленивый разработчик не добавил информацию "
                    "о ней. Используйте на свой страх и риск.", ephemeral=True)
            embed = disnake.Embed(title=f"❔ | О команде `/{cmd}`", color=Color.primary)
            embed.description = """
`<обязательный параметр>` `[необязательный параметр]`
**Не используйте скобочки при указании параметров**
            """
            embed.add_field(inline=False, name="Описание", value=">>> " + data[cmd]["description"] + ".")
            if len(data[cmd]["args"]):
                embed.add_field(inline=False, name="Параметры",
                                value=">>> " + "\n".join([f"`{a}`" for a in data[cmd]["args"]]))
            if len(data[cmd]["examples"]):
                embed.add_field(inline=False, name="Примеры использования",
                                value=">>> " + "\n".join([f"`/{a}`" for a in data[cmd]["examples"]]))
            if len(disnake.utils.get(self.bot.commands, name=cmd).aliases):
                embed.add_field(inline=False, name="Алиасы (синонимы)", value=">>> " + ", ".join(
                    [f"`{a}`" for a in disnake.utils.get(self.bot.commands, name=cmd).aliases]))
            await interaction.send(embed=embed, ephemeral=True)

    @commands.slash_command(name="invite", description="Приглашение бота на сервер")
    @commands.check(src.messages.check_perms)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def invite(self, interaction: disnake.UserCommandInteraction):
        embed = disnake.Embed(title="🔗 | Ссылки", color=Color.primary)
        embed.description = '''
[🤖 Пригласить бота](https://disnake.com/api/oauth2/authorize?client_id=1011518795954782238&permissions=8&scope=bot)
[❔ Поддержка](https://disnake.gg/U4ge8Fup5u)
[🌐 Сайт](https://crash-protect.github.io/crash-protect/)
        '''
        await interaction.send(embed=embed)

    @commands.slash_command(name="serverinfo", description="Информация о сервере")
    @commands.check(src.messages.check_perms)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def server(self, interaction: disnake.UserCommandInteraction):
        embed = disnake.Embed(title=f'🌍 | Информация о сервере **{interaction.guild.name}**', color=Color.primary)
        if interaction.guild.icon:
            embed.set_thumbnail(url=interaction.guild.icon.url)
        vlevels = {
            'none': ':white_circle: Отсутствует',
            'low': ':green_circle: Низкий',
            'medium': ':yellow_circle: Средний',
            'high': ':orange_circle: Высокий',
            'extreme': ':red_circle: Самый высокий'
        }
        embed.add_field(name='Роли', value=f'''
> Всего: **{len(interaction.guild.roles)}**
> С правами администратора: **{len([r for r in interaction.guild.roles if r.permissions.administrator])}**
> С правами модератора: **{len([r for r in interaction.guild.roles if r.permissions.kick_members])}**
> Интеграций: **{len([r for r in interaction.guild.roles if r.managed])}**
        ''')
        embed.add_field(name='Каналы', value=f'''
> Всего: **{len([c for c in interaction.guild.channels if not isinstance(c, disnake.CategoryChannel)])}**
> Текстовых: **{len(interaction.guild.text_channels)}**
> Голосовых: **{len(interaction.guild.voice_channels)}**
> Категорий: **{len(interaction.guild.categories)}**
        ''')
        embed.add_field(name='Участники', inline=False, value=f'''
> Всего: **{len(interaction.guild.members)}**
> Людей: **{len([m for m in interaction.guild.members if not m.bot])}**
> Ботов: **{len([m for m in interaction.guild.members if m.bot])}**
> Админов: **{len([m for m in interaction.guild.members if m.guild_permissions.administrator])}**
> Модераторов: **{len([m for m in interaction.guild.members if m.guild_permissions.kick_members])}**
        ''')
        dt = interaction.guild.created_at.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)
        if not interaction.guild.owner:
            oww = "**Не кэширован**"
        else:
            oww = f"**{interaction.guild.owner}** ({interaction.guild.owner.mention})"
        embed.add_field(name='Прочее', value=f'''
> Владелец: {oww}
> Уровень проверки: **{vlevels[str(interaction.guild.verification_level)]}**
> Дата создания сервера: <t:{int(dt.timestamp())}> (<t:{int(dt.timestamp())}:R>)
        ''')
        if src.messages.has_premium(interaction.guild.id):
            embed.add_field(name="CrashProtect Plus активен!", value="Спасибо за поддержку CrashProtect :heart:",
                            inline=False)
        embed.set_footer(text=f'ID: {interaction.guild.id} | Шард {interaction.guild.shard_id}')
        await interaction.send(embed=embed)

    @commands.command(aliases=['userinfo', 'user-info', 'user_info', 'u'])
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.check(src.messages.check_perms)
    async def user(self, ctx, user: disnake.User = None):
        if user is None:
            user = ctx.author
        embed = disnake.Embed(color=Color.primary)
        if user.bot:
            embed.title = f"🤖 | Информация о боте **{user}**"
        else:
            embed.title = f"👤 | Информация о пользователе **{user}**"
        embed.set_thumbnail(url=user.avatar_url)
        embed.set_footer(text=f'ID: {user.id}')
        if ctx.guild.get_member(user.id):
            user = ctx.guild.get_member(user.id)
            if user.bot:
                try:
                    dob_id = int(src.utils.cache.invited_data[ctx.guild.id][str(user.id)])
                    dob_u = self.bot.get_user(dob_id)
                    if dob_u:
                        embed.add_field(name="Кто добавил", value=dob_u, inline=False)
                except (Exception, BaseException):
                    pass
            embed.add_field(inline=False, name="Роли",
                            value=f'Всего: **{len(user.roles)}**, наивысшая: {user.top_role.mention}')
            if user == ctx.guild.owner:
                embed.add_field(inline=True, name="Владелец сервера?", value='✅ Да')
            else:
                embed.add_field(inline=True, name="Владелец сервера?", value='❌ Нет')
                if user.guild_permissions.administrator:
                    embed.add_field(inline=True, name="Администратор?", value='✅ Да')
                else:
                    embed.add_field(inline=True, name="Администратор?", value='❌ Нет')
            ja = user.joined_at.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)
            embed.add_field(inline=False, name="Дата присоединения к серверу",
                            value=f'<t:{int(ja.timestamp())}> (<t:{int(ja.timestamp())}:R>)')
        ca = user.created_at
        embed.add_field(inline=False, name="Дата создания аккаунта",
                        value=f'<t:{int(ca.timestamp())}> (<t:{int(ca.timestamp())}:R>)')
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.check(src.messages.check_perms)
    async def prefix(self, ctx, prefix):
        if prefix.lower() in ["reset", "сброс", "cp."]:
            if ctx.guild.id in src.utils.cache.configs_data:
                if "prefix" in src.utils.cache.configs_data[ctx.guild.id]:
                    src.utils.cache.configs.delete(ctx.guild.id, {"prefix": True})
                    await ctx.send(embed=disnake.Embed(
                        title="✅ | Готово",
                        description="Префикс успешно сброшен.",
                        color=Color.success
                    ))
                else:
                    await src.messages.err(ctx, "Префикс и так стоит по умолчанию.", True)
            else:
                await src.messages.err(ctx, "Префикс и так стоит по умолчанию.", True)
        else:
            if len(prefix) > 6:
                await src.messages.err(ctx, "Максимальная длина префикса — **6**.", True)
            else:
                src.utils.cache.configs.add(ctx.guild.id, {"prefix": prefix})
                await ctx.send(embed=disnake.Embed(
                    title="✅ | Готово",
                    description=f"Новый префикс — `{prefix}`.",
                    color=Color.success
                ))

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            if message.content.startswith(f'<@{self.bot.user.id}>') or message.content.startswith(
                    f'<@!{self.bot.user.id}>'):
                try:
                    prefix = src.utils.cache.configs_data[message.guild.id]['prefix']
                except (Exception, BaseException):
                    prefix = 'cp.'
                await message.channel.send(
                    f'{message.author.mention}, мой префикс – `{prefix}`. '
                    f'Для просмотра списка команд введи `{prefix}help`.')

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.check(src.messages.check_perms)
    async def info(self, ctx):
        if Other.uptime == 0:
            uptime2 = 0
        else:
            uptime2 = int(time.time()) - Other.uptime
        embed = disnake.Embed(title="ℹ | Инфо",
                              description="Здравствуй здравствуй здравстуй, рад видеть тебя! Мой замечательный "
                                          "пользователь, я ~~расскажу тебе сказку~~ анти краш бот и буду тебе "
                                          "защищать сервер;)",
                              color=Color.primary)
        if Other.shard_count <= 2:
            embed.add_field(
                name="Система",
                inline=False,
                value=f'''
    🪁 Средняя задержка бота: **{int(self.bot.latency * 1000)} мс**
    ⏳ Аптайм: **{src.word.hms(uptime2)}**
    🌠 Команд выполнено: **{src.utils.cache.botstats_data[self.bot.user.id]["commands_completed"]}**
                '''
            )
        else:
            embed.add_field(
                name="Система",
                inline=False,
                value=f'''
    🪁 Средняя задержка бота: **{int(self.bot.latency * 1000)} мс**
    ⏳ Аптайм: **{src.word.hms(uptime2)}**
    🌈 Шардов: **{len(self.bot.shards)}**
    🆔 ID шарда этого сервера: **{ctx.guild.shard_id}**
    🌠 Команд выполнено: **{src.utils.cache.botstats_data[self.bot.user.id]["commands_completed"]}**
                '''
            )
        embed.add_field(
            name="Серверы",
            inline=False,
            value=f'''
🌀 Количество: **{len(self.bot.guilds)}**
🥇 Крупных серверов (1000+): **{len([g for g in self.bot.guilds if g.member_count >= 1000])}**
👦🏼 Пользователей: **{len(self.bot.users)}**
            '''
        )
        embed.add_field(
            name="Прочее",
            inline=False,
            value=f'''
📆 Дата создания: **31 августа 1820 года**
🐍 Версия Python: **3.10**
📄 Версия: **1.5 (23 августа 2022 года)**
👨‍💻 Разработчики: **S.mode#9723**
            '''
        )
        embed.add_field(
            name="Ссылки",
            inline=False,
            value=f'''
[Пригласить бота](https://disnake.com/api/oauth2/authorize?client_id=1011518795954782238&permissions=8&scope=bot)
[Сервер поддержки](https://disnake.gg/sf7UwMWFB2)
[Сайт бота](https://crash-protect.github.io/crash-protect/)
            '''
        )
        embed.add_field(
            name="Благодарность",
            inline=False,
            value=f'''
**Cymon#4380** - за оригинальный код бота и аватарку боту, благодаря ему вы сейчас наблюдаете этого бота.
**Artem Bay#0547** - внёс вклад в бота и исправил шарды.
**самсунг ассистент#8068** - плахой мальчик, но в какой-то степени из-за него тоже вы наблюдаете сейчас этого бота.
**S.mode#9723** - новый владелец Crash Protect. Он дорабатывает и исправляет анти краш бота Crash Protect.
            '''
        )
        embed.set_footer(text="© 2022, S.mode | Все права защищены ботом Crash Protect",
                         icon_url=self.bot.get_user(711844449533165618).avatar.url if self.bot.get_user(
                             711844449533165618).avatar else self.bot.user.avatar.url)
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.check(src.messages.check_perms)
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def ping(self, ctx):
        embed = disnake.Embed(title="🏓 | Понг!", description=f'Средняя задержка: **{int(self.bot.latency * 1000)} мс**',
                              color=Color.primary)
        if Other.shard_count == 2:
            embed.add_field(inline=False, name="По шардам:", value=f'''
    Шард **0**: **{int(self.bot.get_shard(0).latency) * 1000}мс**
    Шард **1**: **None мс**
    Шард **2**: **None мс**
    Шард **3**: **None мс**
    Шард **4**: **None мс**
    Шард **5**: **None мс**
    Шард **6**: **None мс**
    Шард **7**: **None мс**
            ''')
            embed.set_footer(text=f'ID вашего шарда: {ctx.guild.shard_id}')
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Cmd(bot))
