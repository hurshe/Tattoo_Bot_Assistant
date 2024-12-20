import os
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot_app.db_manager import DBManager
from bot_app.conversation_handler import user_answers
from bot_app.chat_actions import delete_messages

load_dotenv()
admin_chat_id = os.getenv('ADMIN_ID')
sub_admin_id = os.getenv('SUB_ADMIN_ID')

db = DBManager('tattoo_bot_telegram.db')


class AdminCommands:
    """
    AdminCommands Class Description

    The `AdminCommands` class encapsulates a set of static methods tailored for administrative tasks within a Telegram 
    bot application. These methods enable administrators to manage vouchers, view statistics, and perform other 
    administrative actions. Each method handles specific functionalities, ensuring efficient administration and user 
    interaction.
    
    Attributes: - None within the class itself, but the class utilizes external resources such as image paths for
    sending media content.
    
    Static Methods:
    
    1. `admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE)`
       - Handles the main administrative command, displaying a menu of available admin options based on user privileges.
       - Checks if the user is an admin or sub-admin and sends appropriate menu options.
       
    2. `add_voucher(update: Update, context: ContextTypes.DEFAULT_TYPE)`
       - Initiates the process of adding a new voucher to the system by prompting the admin for voucher details.
       - Provides instructions on how to add a voucher and cancel the operation if needed.
    
    3. `accept_add_voucher(update: Update, context: ContextTypes.DEFAULT_TYPE)`
       - Validates and adds a new voucher to the system if it does not already exist.
       - Notifies the admin of success or failure in adding the voucher.
    
    4. `statistics_command(update: Update, context: ContextTypes.DEFAULT_TYPE)` - Displays statistical
    information related to voucher usage and sales. - Provides insights into the number of people who have used the 
    bot, total vouchers sold, total sales amount, and the latest sale.
    
    5. `view_all_active_vouchers(update: Update, context: ContextTypes.DEFAULT_TYPE)`
       - Displays all active vouchers available in the system.
       - Allows the admin to navigate through the list of active vouchers.
    
    6. `view_selected_active_voucher(update: Update, context: ContextTypes.DEFAULT_TYPE)`
       - Provides detailed information about a selected active voucher.
       - Allows the admin to activate the selected voucher for use.
    
    7. `view_selected_deactivate_voucher(update: Update, context: ContextTypes.DEFAULT_TYPE)`
       - Displays details of all deactivated vouchers.
       - Notifies if there are no deactivated vouchers available.
    
    8. `activate_voucher(update: Update, context: ContextTypes.DEFAULT_TYPE)`
       - Activates a selected voucher for use.
       - Notifies the admin upon successful activation of the voucher.
    
    9. `send_db_file_in_chat(update: Update, context: ContextTypes.DEFAULT_TYPE)`
       - Sends the database file to the chat.
       - Allows the admin to retrieve the database file for external use or backup purposes.
    
    Usage: - These static methods can be called within the context of a Telegram bot application to perform various
    administrative tasks such as managing vouchers, viewing statistics, and accessing the database. Each method provides 
    specific functionalities to streamline the administration process and enhance user experience.
    
    Note: This class assumes integration with a Telegram bot application and utilizes external resources such as
    image paths for media content."""
    
    @staticmethod
    async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        admin = [int(admin_chat_id), int(sub_admin_id)]

        await delete_messages(update, context)

        if chat_id in admin:
            check_voucher_button = InlineKeyboardButton('🎁 Просмотреть активные ваучеры', callback_data='check_voucher')
            check_deactivated_voucher_button = InlineKeyboardButton('❌Просмотреть неактивыне ваучеры',
                                                                    callback_data='activated')
            add_voucher_button = InlineKeyboardButton('➕ Добавить новый ваучер', callback_data='add_voucher')
            show_statistics_button = InlineKeyboardButton('📊 Показать статистику', callback_data='statistics')
            get_db_file_in_chat_btn = InlineKeyboardButton('🗃️ Получить файл с базой данных', callback_data='db_in_chat')
            all_commands_button = InlineKeyboardButton('🤖Вернуться в главное меню', callback_data='all_commands')

            keyboard = InlineKeyboardMarkup([[check_voucher_button],
                                             [check_deactivated_voucher_button],
                                             [add_voucher_button],
                                             [show_statistics_button],
                                             [get_db_file_in_chat_btn],
                                             [all_commands_button]])

            await context.bot.send_photo(chat_id=chat_id, photo=img_path.get('admin_image'), reply_markup=keyboard)
        else:
            back_button = InlineKeyboardButton('⏪ Назад', callback_data='all_commands')
            keyboard = InlineKeyboardMarkup([[back_button]])

            await context.bot.send_photo(chat_id=chat_id, photo='bot_app/media/denied.jpg',
                                         caption="Отказано в доступе. Access Denied. Odmowa dostępu.",
                                         reply_markup=keyboard)

    @staticmethod
    async def add_voucher(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id

        back_button = InlineKeyboardButton('⏪ Назад', callback_data='admin')
        keyboard = InlineKeyboardMarkup([[back_button]])

        await delete_messages(update, context)
        await context.bot.send_message(chat_id=chat_id,
                                       text='Команда [/add] запросит данные для нового ваучера.\n'
                                            'Команда [/cancel] отменит запись нового ваучера.\n\n'
                                            'После записи данных вы сможете просмотреть и активировать добавленые '
                                            'вами и '
                                            'ботом ваучеры в базе.\n '
                                            'Используя команду /admin', reply_markup=keyboard)

    @staticmethod
    async def accept_add_voucher(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        selected_voucher = user_answers.get('question_1')
        vouchers_in_db = db.get_all_active_voucher_code()
        vouchers_in_db = [item[0] for item in vouchers_in_db]
        admin = [int(admin_chat_id), int(sub_admin_id)]

        back_btn = InlineKeyboardButton('⏪ BACK', callback_data='all_commands')
        keyboard = InlineKeyboardMarkup([[back_btn]])

        if chat_id not in admin:
            await context.bot.send_photo(chat_id=chat_id, photo='media/denied.jpg',
                                         caption="Отказано в доступе. Access Denied. Odmowa dostępu.",
                                         reply_markup=keyboard)
        else:
            if selected_voucher in vouchers_in_db:
                await context.bot.send_message(chat_id=chat_id,
                                               text="Такой код уже существует, попробуйте еще раз! /add")
            else:
                await context.bot.send_message(chat_id=chat_id,
                                               text=f"Ваучер с кодом  {selected_voucher}  успешно добавлен в базу")
                return db.add_voucher_to_db(chat_id)
            return db.delete_data_from_db(chat_id)

    @staticmethod
    async def statistics_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        stat_info = db.get_statistics_of_vouchers(chat_id)

        people = stat_info[0] if stat_info is not None else '0'
        sold_vouchers = stat_info[1] if stat_info is not None else '0'
        amount_sales = stat_info[2] if stat_info is not None else '0'
        last_sold_voucher = stat_info[3] if stat_info is not None else 'Продаж не было '

        back_button = InlineKeyboardButton('⏪ Назад', callback_data='admin')

        keyboard = InlineKeyboardMarkup([[back_button]])

        await delete_messages(update, context)
        await context.bot.send_photo(chat_id=chat_id,
                                     photo=img_path.get('stat_image'),
                                     caption=f"🧍 Людей посетило TattooBotAssistant:\n"
                                             f"-------->  {people} человек\n"
                                             f"🔥 Ваучеров было проданно вообщем:\n"
                                             f"-------->  {sold_vouchers} ваучеров\n"
                                             f"💰 Сумма общей продажи от ваучеров:\n"
                                             f"-------->  {amount_sales} PLN\n"
                                             f"📆 Была совершена последняя покупка:\n"
                                             f"-------->  {last_sold_voucher}",
                                     reply_markup=keyboard)

    @staticmethod
    async def view_all_active_vouchers(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        active_vouchers = db.get_all_active_voucher_code()

        buttons = {item[0]: item[0] for item in active_vouchers}
        buttons["⏪ Назад"] = "admin"
        buttons_per_row = 3

        keyboard_buttons = [
            [
                InlineKeyboardButton(button_text, callback_data=callback_data)
                for button_text, callback_data in buttons.items()
            ][i:i + buttons_per_row]
            for i in range(0, len(buttons), buttons_per_row)

        ]

        keyboard_markup = InlineKeyboardMarkup(keyboard_buttons)

        await delete_messages(update, context)

        if not active_vouchers:
            await context.bot.send_photo(chat_id=chat_id, photo=img_path.get('empty_data'),
                                         caption="Пока купленных ваучеров нет.", reply_markup=keyboard_markup)
        else:
            await context.bot.send_photo(chat_id=chat_id, photo=img_path.get('active_vouchers_img'),
                                         caption='✅ Все активные ваучеры (еще не использованые).',
                                         reply_markup=keyboard_markup)

    @staticmethod
    async def view_selected_active_voucher(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        selected_voucher = db.get_selected_voucher(chat_id)
        price_of_selected_voucher = db.get_price_voucher(chat_id, selected_voucher)

        activate_button = InlineKeyboardButton('ACTIVATE', callback_data='activate')
        back_button = InlineKeyboardButton('⏪ Назад', callback_data='check_voucher')

        keyboard = InlineKeyboardMarkup([[activate_button], [back_button]])

        await delete_messages(update, context)
        await context.bot.send_message(chat_id=chat_id,
                                       text=f"Вы выбрали ваучер:\n\n"
                                            f"ID:  {selected_voucher}\n"
                                            f"Цена: {price_of_selected_voucher} PLN\n\n"
                                            f"Выберите [ACTIVATE] для активации ваучера.\n"
                                            f"❗ВАЖНО - После активации ваучер станет не пригодным\n"
                                            f"и будет находиться в базе как использованый ваучер!\n"
                                            f"В /admin панели есть функция 'Просмотреть использованые ваучеры'",
                                       reply_markup=keyboard)

    @staticmethod
    async def view_selected_deactivate_voucher(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        selected_deactivate_voucher = db.get_deactivate_voucher(chat_id)

        back_button = InlineKeyboardButton('⏪ Назад', callback_data='admin')
        keyboard = InlineKeyboardMarkup([[back_button]])

        voucher_message = 'Вот все использованые ваучеры:\n'

        await delete_messages(update, context)

        if not selected_deactivate_voucher:
            await context.bot.send_photo(chat_id=chat_id,
                                         photo=img_path.get('empty_data'),
                                         caption='Пока активированых ваучеров нет!',
                                         reply_markup=keyboard)
        else:
            for voucher_data in selected_deactivate_voucher:
                voucher_message += f'❌\nID: {voucher_data[0]}\nValue: {voucher_data[1]}\nDate: {voucher_data[2]}\n'

            await context.bot.send_photo(chat_id=chat_id,
                                         photo=img_path.get('active_vouchers_img'),
                                         caption=voucher_message,
                                         reply_markup=keyboard)

    @staticmethod
    async def activate_voucher(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        selected_voucher = db.get_selected_voucher(chat_id)
        activate = db.activate_voucher(chat_id)
        await context.bot.send_message(chat_id=chat_id, text=f"Ваучер:  {selected_voucher}  был активирован!")
        return activate

    @staticmethod
    async def send_db_file_in_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        db_file = '/tattoo_bot_telegram.db'

        await context.bot.send_document(chat_id=chat_id, document=db_file)


img_path = {
    'admin_image': 'bot_app/media/admin_image.jpg',
    'admin_error': 'bot_app/media/denied.jpg',
    'active_vouchers_img': 'bot_app/media/active_voucher.jpg',
    'empty_data': 'bot_app/media/empty_data.jpg',
    'stat_image': 'bot_app/media/statistic_photo.jpg'
}
