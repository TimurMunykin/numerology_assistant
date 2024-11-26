import os
import logging
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler
from dotenv import load_dotenv

from src.find import get_answer

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

user_debug_modes = {}
# Словарь для хранения индекса последнего показанного ответа для каждого пользователя
user_answer_indexes = {}
answers = None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        parse_mode=telegram.constants.ParseMode.MARKDOWN_V2,
        text='''
👋 Привет\! Я \- бот\-нумеролог, специалист по цифровым тайнам\!
Попробуй задать мне вопрос по нумерологии, например:
```
Какой источник удачи у человека с числом жизненого пути 4
```

```
Какая у меня совместимость с партнером
```

```
Дай мне логику расчета номер души
```
Я готов удивлять тебя ответами\! ✨
'''
    )
    """Sends a message with three inline buttons attached."""


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global answers
    user_id = update.effective_user.id
    user_answer_indexes[user_id] = 0  # Инициализация индекса для нового запроса

    await context.bot.send_message(chat_id=update.effective_chat.id, text='🤔 Дай мне секундочку, я подумаю...')

    try:
        api_key = os.getenv('OPEN_AI_API_KEY')
        answers = get_answer(question=update.message.text, api_key=api_key)
        await send_answers(update, context, user_id)  # Вызов функции отправки ответов

    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Ошибка: {e}')


async def send_answers(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    global answers
    start_index = user_answer_indexes.get(user_id, 0)
    end_index = min(start_index + 5, len(answers))

    for index in range(start_index, end_index):
        answer = answers.iloc[index]
        button = InlineKeyboardButton("Открыть методику", callback_data=f"{index}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=answer.topicText, reply_markup=InlineKeyboardMarkup([[button]]))

    if end_index < len(answers):
        next_button = InlineKeyboardButton("Следующие 5 методик", callback_data=f"next_{end_index}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Есть еще методики. Нажмите кнопку для продолжения.',
            reply_markup=InlineKeyboardMarkup([[next_button]])
        )

    user_answer_indexes[user_id] = end_index


async def enable_debug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_debug_modes[user_id] = True
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Debug mode *enabled* for you\.",
        parse_mode=telegram.constants.ParseMode.MARKDOWN_V2
    )


async def disable_debug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_debug_modes[user_id] = False
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Debug mode *disabled* for you\.",
        parse_mode=telegram.constants.ParseMode.MARKDOWN_V2
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global answers
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    if query.data.startswith("next_"):
        next_index = int(query.data.split("_")[1])
        user_answer_indexes[user_id] = next_index
        await send_answers(update, context, user_id)
    else:
        index = int(query.data)
        answer = answers.iloc[index]
        await query.edit_message_text(text=f"{answer.topicText}: {answer.topicNotes}")


def main():
    load_dotenv()
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    application = ApplicationBuilder().token(token).build()

    start_handler = CommandHandler('start', start)
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    enable_debug_handler = CommandHandler('enable_debug', enable_debug)
    disable_debug_handler = CommandHandler('disable_debug', disable_debug)

    application.add_handler(start_handler)
    application.add_handler(message_handler)
    application.add_handler(enable_debug_handler)
    application.add_handler(disable_debug_handler)
    application.add_handler(CallbackQueryHandler(button))

    application.run_polling()


main()
