import os
import dotenv
import logging
from typing import Final

from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
from telegram import Update

from bot_app.conversation_handler import add_voucher_command, cancel, question_1, question_2

from bot_app.admin_commands import AdminCommands
from bot_app.commands import MainMenuCommands
from bot_app.data_handler import button_click
from bot_app.db_manager import DBManager

dotenv.load_dotenv()

TOKEN: Final = os.getenv('TOKEN')
BOT_USERNAME: Final = os.getenv("BOT_USERNAME")

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

conv_handler = ConversationHandler(
        entry_points=[CommandHandler('add', add_voucher_command)],
        states={
            'question_1': [MessageHandler(filters.TEXT & ~filters.COMMAND, question_1)],
            'question_2': [MessageHandler(filters.TEXT & ~filters.COMMAND, question_2)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

db_manager = DBManager('tattoo_bot_telegram.db')
admin = AdminCommands()
main_commands = MainMenuCommands()

if __name__ == "__main__":
    print('Start polling...')

    conn = db_manager.create_connection()
    if conn is not None:
        db_manager.create_users_table()
        db_manager.create_vouchers_table()
        conn.close()
        print('Tables was created successfully')
    else:
        print("Ошибка! Невозможно подключиться к базе данных.")

    bot_app = Application.builder().token(TOKEN).build()

    bot_app.add_handler(CommandHandler('start', main_commands.start_command))
    bot_app.add_handler(CommandHandler('admin', admin.admin_command))
    bot_app.add_handler(CallbackQueryHandler(button_click))
    bot_app.add_handler(conv_handler)
    print('Polling...')

    bot_app.run_polling(allowed_updates=Update.ALL_TYPES)





