import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackContext,
    CallbackQueryHandler,
)

# Включаем логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# задаём логирование для httpx чтобы избежать всех GET и POST запросов в логе.
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Сохранение логирования действий бота
# Создаем обработчик для сохранения логов в файл
war_handler = logging.FileHandler('botINFO.log')
war_handler.setLevel(logging.INFO)
info_handler = logging.FileHandler('botWARNING.log')
info_handler.setLevel(logging.WARNING)

# Форматирование сообщений лога уровня INFO и WARNING
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
war_handler.setFormatter(formatter)
info_handler.setFormatter(formatter)

# Добавляем обработчики к логгеру
logger.addHandler(war_handler)
logger.addHandler(info_handler)

# Задаём переменные: токен бота, ID группы куда выводить сообщения
bottoken = ''
Group_id = ''

HELP = 0
INPUT_TEXT = 0


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    await update.message.reply_text(
        f"Доброго времени суток {user.first_name} опишите что у вас случилось!"
    )
    return HELP

async def send_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    user_id = update.message.from_user.id
    message = update.message.text
    logger.info("Пользователь: %s; c ID номером  %s. отправил заявку", user.first_name, update.effective_user.id)
    button = InlineKeyboardButton(text="Написать пользователю", callback_data=str(user_id))
    keyboard = InlineKeyboardMarkup([[button]])
    # Проверяем: если есть текст
    if update.message.text:
        await context.bot.send_message(chat_id=Group_id,
                                       text=f'Новое сообщение \n <b>Пользователь:</b> {user.first_name}\n '
                                             f'<b>ID номер: </b><code>{update.effective_user.id}</code>\n '
                                            f'<b>Текст сообщения:</b>\n   {update.message.text}',
                                       reply_markup=keyboard,
                                       parse_mode='HTML')
    # если есть фото
    if update.message.photo:
        photo_file_id = update.message.photo[-1].file_id
        caption = update.message.caption
        await context.bot.send_message(chat_id=Group_id,
                                       text=f'Новое сообщение \n <b>Пользователь:</b> {user.first_name}\n '
                                            f'<b>ID номер: </b><code>{update.effective_user.id}</code>\n '
                                            f'<b>Текст сообщения ниже под загруженным фото:</b>\n',
                                       parse_mode='HTML')
        await context.bot.send_photo(chat_id=Group_id, photo=photo_file_id, caption=caption, reply_markup=keyboard)



    # Отвечаем пользователю
    await update.message.reply_text(f"Ваше сообщение отправлено! Пожалуйста, дождитесь сообщения от специалиста!")
    return ConversationHandler.END

async def ask_for_text(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    user_id = query.data
    context.user_data['user_id'] = user_id
    await update.effective_message.reply_text('Пожалуйста, введите текст или прикрепите файл с описанием, который вы хотите отправить:')

    return INPUT_TEXT


async def send_message_by_id(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    user_id = context.user_data['user_id']
    # если есть текст
    if update.message.text:
        await context.bot.send_message(chat_id=user_id, text=text)
    # если есть фото
    if update.message.photo:
        photo_file_id = update.message.photo[-1].file_id
        caption = update.message.caption
        await context.bot.send_photo(chat_id=user_id, photo=photo_file_id, caption=caption)


    await update.message.reply_text(f"Ваше сообщение отправлено!")
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("Пользователь %s отменил действие.", user.first_name)
    await update.message.reply_text(
        "Действите отклонено",
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    message = update.message.text
    logger.info("Пользователь: %s; запросил свой ID  %s.", user.first_name, update.effective_user.id)
    await update.message.reply_text(
        f"Ваш ID: {update.effective_user.id}".format(update.effective_user.id),
        reply_markup=ReplyKeyboardRemove()
    )

def main() -> None:
    try:
        # Создание Application и задаём токен бота.
        application = Application.builder().token(bottoken).build()

        # Создаем Conversation и обявляет точки message, done в одном и help, send_help в другом

        conv_handler_help = ConversationHandler(
            entry_points=[CommandHandler("help", help)],
            states={
                HELP: [MessageHandler(filters.TEXT | filters.PHOTO, send_help)],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
        )
        conv_handler_send = ConversationHandler(
            entry_points=[CallbackQueryHandler(ask_for_text, pattern='^\\d+$')],
            states={
                INPUT_TEXT: [MessageHandler(filters.TEXT | filters.PHOTO, send_message_by_id)],
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )

        application.add_handler(CommandHandler("myid", myid))
        application.add_handler(conv_handler_help)
        application.add_handler(conv_handler_send)

        # Run the bot until the user presses Ctrl-C
        application.run_polling(allowed_updates=Update.ALL_TYPES)


    except Exception as e:
        logger.error("Exception occurred: %s", str(e))


if __name__ == "__main__":
    main()
