from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, filters, ConversationHandler, CallbackQueryHandler, Application
import logging
import asyncio

# Устанавливаем уровень логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

#my_queue = Queue()


# Определяем стартовую команду
async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    try:
        await update.message.reply_photo(open('main_photo.jpg', 'rb'), caption=f"День добрый, {user.first_name}, чем могу помочь?", reply_markup=ReplyKeyboardMarkup([["Проблемы с 1С"], ["Проблемы с компьютером"], ["Проблемы с телеметрией"], ["Проблемы инного характера"]], one_time_keyboard=True))
    except Exception as e:
        logger.error("Exception occurred: %s", str(e))

# Обработка нажатия кнопок
async def button(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    text = update.message.text
    user_id = update.effective_user.id
    if text == 'Проблемы с 1С':
        await context.bot.send_message(chat_id=1366168849, text=f"Описание проблемы с 1С... у пользователя {user.first_name} c ID {user_id}")
    elif text == 'Проблемы с компьютером':
        await context.bot.send_message(chat_id=user_id, text="Описание проблемы с компьютером...")
    elif text == 'Проблемы с телеметрией':
        await context.bot.send_message(chat_id=user_id, text="Описание проблемы с телеметрией...")
    elif text == 'Узнать свой ID':
        await context.bot.send_message(chat_id=1366168849, text=f"Ваш ID в телеграмме: {user_id}")

# Обработка текстовых сообщений
#async def echo(update: Update, context: CallbackContext) -> None:
   # await update.message.reply_text("Пожалуйста, воспользуйтесь кнопками для выбора категории.")

def main() -> None:
    try:

        application = Application.builder().token("YOUR_TOKEN").build()

        # Регистрируем обработчики
        application.add_handler(CommandHandler("start", start))
        #application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
        application.add_handler(MessageHandler(filters.Regex('^(Проблемы с 1С|Проблемы с компьютером|Проблемы с телеметрией|Проблемы инного характера)$'), button))

        # Запускаем бота
        application.run_polling(allowed_updates=Update.ALL_TYPES)
		
    except Exception as e:
        logger.error("Exception occurred: %s", str(e))

if __name__ == '__main__':
    main()
	
