import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# Задаём переменные: токен бота, ID группы куда выводить сообщения
bottoken = ''
Group_id = ''

"""
#Сохранение логирования действий бота
# Создаем обработчик для сохранения логов в файл
file_handler = logging.FileHandler('bot.log')
file_handler.setLevel(logging.INFO)

# Создаем обработчик для вывода логов в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Форматирование сообщений лога
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Добавляем обработчики к логгеру
logger.addHandler(file_handler)
logger.addHandler(console_handler)
"""


ID, MESSAGE = range(2)
HELP = range(1)



async def send(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    logger.info("Пользователь: %s; собирается писать что-то", user.first_name)
    await update.message.reply_text(f"{user.first_name} отправляет сообщение. Введите ID собеседника:")
	
    return ID


async def message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    user_id = update.message.text
    context.user_data['user_id'] = user_id
    logger.info("Пользователь: %s; выбрал ID получателя: %s.", user.first_name, user_id)
    await update.message.reply_text(
        "Теперь введите текст сообщения:"
    )

    return MESSAGE


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
            user = update.effective_user
            message = update.message.text
            user_id = context.user_data['user_id']
            logger.info("Пользователь: %s; отправил сообщение ID получателю: %s.", user.first_name, user_id)
            await context.bot.send_message(chat_id=user_id, text=message)
            await update.message.reply_text(
                "Сообщение успешно отправлено!",
                reply_markup=ReplyKeyboardRemove()
            )
    except Exception as e:
        logger.error("Ошибка при отправке сообщения: %s", str(e))
        await update.message.reply_text("Диалога с таким пользователем нет.")
    except Exception as e:
        logger.error("Произошла ошибка: %s", str(e))
        await update.message.reply_text("Произошла ошибка при отправке сообщения.")
    
    return ConversationHandler.END
    
async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    message = update.message.text
    logger.info("Пользователь: %s; запросил свой ID  %s.", user.first_name, update.effective_user.id)
    await update.message.reply_text(
        f"Ваш ID: {update.effective_user.id}".format(update.effective_user.id),
        reply_markup=ReplyKeyboardRemove()
    )
	
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    await update.message.reply_text(
        f"Доброго времени суток {user.first_name} опишите что у вас случилось!"
    )
    return HELP	
	
async def send_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    message = update.message.text
    logger.info("Пользователь: %s; c ID номером  %s. отправил заявку", user.first_name, update.effective_user.id)
    await context.bot.send_message(chat_id=Group_id, text=f"Новое сообщение \n Пользователь: {user.first_name}\n ID номер:{update.effective_user.id}\n Текст сообщения:\n   {update.message.text}")
    await update.message.reply_text(f"Ваше сообщение отправлено! Пожалуйста, дождитесь сообщения от специалиста!")
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


def main() -> None:
    try:
    # Create the Application and pass it your bot's token.
        application = Application.builder().token(bottoken).build()

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("send", send)],
            states={
                ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, message)],
                MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, done)],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
        )
        conv_handler2 = ConversationHandler(
            entry_points=[CommandHandler("help", help)],
            states={
                HELP: [MessageHandler(filters.TEXT & ~filters.COMMAND, send_help)],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
        )
		
        application.add_handler(CommandHandler("myid", myid))
        #application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, help))
        application.add_handler(conv_handler)
        application.add_handler(conv_handler2)

        # Run the bot until the user presses Ctrl-C
        application.run_polling(allowed_updates=Update.ALL_TYPES)
		
    
    except Exception as e:
        logger.error("Exception occurred: %s", str(e))


if __name__ == "__main__":
    main()
