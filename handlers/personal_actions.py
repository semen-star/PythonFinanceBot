from aiogram import types
from dispatcher import dp
import config
import logging
import re
from bot import BotDB
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.message import ContentType
bot = Bot(token=config.BOT_TOKEN)

# log
logging.basicConfig(level=logging.INFO)

# prices
PRICE = types.LabeledPrice(label="Донат 50 рублей", amount=50 * 100)  # в копейках (руб)


@dp.message_handler(commands = "start")#start
async def start(message: types.Message):
    if(not BotDB.user_exists(message.from_user.id)):
        BotDB.add_user(message.from_user.id)

    await message.bot.send_message(message.from_user.id, "Добро пожаловать!\nДля помощи вы можете ввести /help или начать вводить комманды сразу.\n\nP.S. вы были успешно добавленны в базу данных")

@dp.message_handler(commands = "help")#help
async def start(message: types.Message):
    await message.bot.send_message(message.from_user.id, "<u><b>Я здесь, чтобы вам помочь!!</b></u>\n\n\n"
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
                                                         "P.S. поддержать автора можно на карту: 2200700150235868\n"
                                                         "Создатель: @AHAPXICT")

# buy
@dp.message_handler(commands=['donate'])
async def buy(message: types.Message):
    if config.PAYMENTS_TOKEN.split(':')[1] == 'TEST':
        await bot.send_message(message.chat.id, "Тестовый платеж!!!")

    await bot.send_invoice(message.chat.id,
                           title="Донат автору на развитие бота",
                           description="Донат автору в размере 50 рублей",
                           provider_token=config.PAYMENTS_TOKEN,
                           currency="rub",
                           photo_url="https://sun9-61.userapi.com/impg/90MbDe2FhosNxSDBHWhytNkT4s_KAPlNS2nHYg/sU39vkdzcT0.jpg?size=1200x706&quality=95&sign=ed51927b6e10ebcda830a69824a8094b&type=album",
                           photo_width=416,
                           photo_height=234,
                           photo_size=416,
                           is_flexible=False,
                           prices=[PRICE],
                           start_parameter="one-month-subscription",
                           payload="test-invoice-payload")


# pre checkout  (must be answered in 10 seconds)
@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


# successful payment
@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    print("SUCCESSFUL PAYMENT:")
    payment_info = message.successful_payment.to_python()
    for k, v in payment_info.items():
        print(f"{k} = {v}")

    await bot.send_message(message.chat.id,
                           f"Платёж на сумму {message.successful_payment.total_amount // 100} {message.successful_payment.currency} прошел успешно!!!")


@dp.message_handler(commands = ("donate", "d"), commands_prefix = "/!")#balance
async def start(message: types.Message):
    await message.bot.send_message(message.from_user.id, "Извините, функция пока в разаработке. Вы можете связаться с автором и помочь ему.\n\n@AHAPXlCT" )


@dp.message_handler(commands = ("spent", "earned", "s", "e"), commands_prefix = "/!")# Доход/ расход
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

@dp.message_handler(commands = ("history", "h"), commands_prefix = "/!")#history
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