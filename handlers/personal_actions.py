from aiogram import types
from dispatcher import dp
import config
import re
from bot import BotDB

@dp.message_handler(commands = "start")
async def start(message: types.Message):
    if(not BotDB.user_exists(message.from_user.id)):
        BotDB.add_user(message.from_user.id)

    await message.bot.send_message(message.from_user.id, "Добро пожаловать!\nДля помощи вы можете ввести /help или начать вводить комманды сразу.\n\nP.S. вы были успешно добавленны в базу данных")

@dp.message_handler(commands = "help")
async def start(message: types.Message):
    await message.bot.send_message(message.from_user.id, "Я здесь, чтобы вам помочь!!\n\n\n"
                                                         "Чтобы записать расход вы можете воспользоваться коммандами:\n"
                                                         "/s /spent !s !spent\n"
                                                         "Также не забудьте указать сумму. Например: !spent 100  \n\n"
                                                         "Чтобы записать доход вы можете воспользоваться коммандами:\n"
                                                         "/e /earned !e !earned\n"
                                                         "Также не забудьте указать сумму. Например: !earned 100  \n\n"
                                                         "Чтобы посмотреть историю операций вы можете воспользоваться коммандами:\n"
                                                         "/history /h !history !h\n"
                                                         "Также не забудьте указать временной отрезок. Например: !history сегодня  \n"
                                                         "По умолчанию мы будем выводить историю за сегодняшний день. Доступные комманды:\n"
                                                         "today, day,сегодня, день. Месяц, month. year, год\n\n"
                                                         "Также вы можете вывести это сообщение коммандой /help\n\n\n"
                                                         "P.S. поддержать автора можно на карту: 2200700150235868"

                                   )


@dp.message_handler(commands = ("spent", "earned", "s", "e"), commands_prefix = "/!")
async def start(message: types.Message):
    cmd_variants = (('/spent', '/s', '!spent', '!s'), ('/earned', '/e', '!earned', '!e'))
    operation = '-' if message.text.startswith(cmd_variants[0]) else '+'

    value = message.text
    for i in cmd_variants:
        for j in i:
            value = value.replace(j, '').strip()

    if(len(value)):
        x = re.findall(r"\d+(?:.\d+)?", value)
        if(len(x)):
            value = float(x[0].replace(',', '.'))

            BotDB.add_record(message.from_user.id, operation, value)

            if(operation == '-'):
                await message.reply("✅ Запись о <u><b>расходе</b></u> успешно внесена!")
            else:
                await message.reply("✅ Запись о <u><b>доходе</b></u> успешно внесена!")
        else:
            await message.reply("Не удалось определить сумму!")
    else:
        await message.reply("Не введена сумма!")

@dp.message_handler(commands = ("history", "h"), commands_prefix = "/!")
async def start(message: types.Message):
    cmd_variants = ('/history', '/h', '!history', '!h')
    within_als = {
        "day": ('today', 'day', 'сегодня', 'день'),
        "month": ('month', 'месяц'),
        "year": ('year', 'год'),
    }

    cmd = message.text
    for r in cmd_variants:
        cmd = cmd.replace(r, '').strip()

    within = 'day'
    if(len(cmd)):
        for k in within_als:
            for als in within_als[k]:
                if(als == cmd):
                    within = k

    records = BotDB.get_records(message.from_user.id, within)

    if(len(records)):
        answer = f"🕘 История операций за {within_als[within][-1]}\n\n"

        for r in records:
            answer += "<b>" + ("➖ Расход" if not r[2] else "➕ Доход") + "</b>"
            answer += f" - {r[3]}"
            answer += f" <i>({r[4]})</i>\n"

        await message.reply(answer)
    else:
        await message.reply("Записей не обнаружено!\n\nПожалуйста введите доход или расход!\nЕсли вы не понимаете как это делать, введите комманду /help или нажмите на синий текст")