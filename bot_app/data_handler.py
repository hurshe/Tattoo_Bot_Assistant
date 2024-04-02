import os
import dotenv
from datetime import date

import stripe
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot_app.admin_commands import AdminCommands
from bot_app.db_manager import DBManager
from bot_app.voucher_handler import VoucherCommands
from bot_app.commands import MainMenuCommands

from bot_app.email_sender import send_email_with_attachment
from bot_app.conversation_handler import cancel
from bot_app.chat_actions import delete_messages


dotenv.load_dotenv()
date_today = date.today()

STRIPE_API_KEY = os.getenv('STRIPE_API_KEY')
stripe.api_key = STRIPE_API_KEY

db = DBManager('tattoo_bot_telegram.db')

admin_commands = AdminCommands()
main_commands = MainMenuCommands()
voucher_commands = VoucherCommands()


async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Button Click Function Description

    The `button_click` function manages user interactions with inline buttons in a Telegram bot application. It
    handles various button clicks by updating user data in the database and triggering appropriate actions based on
    the clicked button.

    Functionality:

    - Retrieves necessary information from the update, such as callback query data, chat ID, message ID,
    and user details. - Establishes a connection to the database and creates a cursor for executing SQL queries. -
    Handles different types of button clicks, including FAQ actions, voucher selections, function actions,
    admin actions, price actions, and language actions. - Updates user data in the database based on the clicked
    button, such as selected language, function, FAQ option, price selection, and voucher selection. - Handles
    language changes by resetting previously selected data. - Commits the changes to the database and closes the
    database connection. - Invokes the `data_controller` function to handle further actions based on the updated user
    data.

    Usage: - This function is designed to be integrated into a Telegram bot application's inline button handling
    logic. - It allows users to interact with the bot by clicking inline buttons and dynamically updates user data
    based on their actions. - The function ensures smooth user experience by managing various interactions seamlessly
    and updating the database accordingly.

    Note: Ensure that the bot has the necessary permissions to interact with inline buttons and access the database.

    Feel free to use and integrate this function into your Telegram bot application for handling inline button clicks
    effectively!"""

    query = update.callback_query
    new_element = query.data
    chat_id = update.effective_chat.id
    message_id = update.effective_message.message_id
    user_name = update.effective_user.first_name
    first_lang = 'LANGUAGE'
    prev_language = 'PREVLANG'
    prev_func = 'start'

    conn = db.create_connection()
    cursor = conn.cursor()

    cursor.execute('''INSERT INTO users 
        (chat_id, message_id, user_name, email, selected_lang, previous_lang,
         selected_func, prev_func, faq_option, selected_price, previous_price, selected_voucher, user_selected_voucher, dark_soul_code)
        SELECT ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        WHERE NOT EXISTS (SELECT 1 FROM users WHERE chat_id = ?)''',
                   (chat_id, message_id, user_name, None, first_lang, prev_language, None, prev_func, None, None, None, None, None, None, chat_id))

    unpacked_voucher_codes = cursor.execute("SELECT voucher_id FROM vouchers").fetchall()
    voucher_codes = [(item[0]) for item in unpacked_voucher_codes]
    user_voucher_codes = [f'{item[0]}-{chat_id}' for item in unpacked_voucher_codes]

    if new_element in actions['faq_actions']:
        faq_option = new_element
        cursor.execute("UPDATE users SET selected_price = ? WHERE chat_id = ?", (None, chat_id))
        cursor.execute("UPDATE users SET faq_option = ? WHERE chat_id = ?", (faq_option, chat_id,))

    elif new_element in user_voucher_codes:
        user_selected_voucher = new_element
        cursor.execute("UPDATE users SET user_selected_voucher = ? WHERE chat_id = ?", (user_selected_voucher, chat_id))
        cursor.execute("UPDATE users SET selected_voucher =? WHERE chat_id = ? ", (None, chat_id))

    elif new_element in voucher_codes:
        selected_voucher = new_element
        cursor.execute("UPDATE users SET selected_price = ? WHERE chat_id = ?", (None, chat_id))
        cursor.execute("UPDATE users SET selected_voucher = ? WHERE chat_id = ?", (selected_voucher, chat_id))

    elif new_element in actions['function_actions'] or new_element in actions['admin_actions']:
        selected_func = new_element
        cursor.execute("UPDATE users SET selected_func = ? Where chat_id = ?", (selected_func, chat_id))

    elif new_element in actions['price_actions']:
        selected_value = new_element
        current_price = db.get_selected_value(chat_id)

        if current_price != selected_value:
            previous_value = current_price

            cursor.execute("UPDATE users SET selected_price = ?, previous_price = ?, selected_voucher = ?, "
                           "user_selected_voucher = ? WHERE chat_id = ?",
                           (selected_value, previous_value, None, None, chat_id,))

    elif new_element in actions['language_actions']:
        selected_lang = new_element
        '''When we change the language we need to remove all data which we choose before'''

        current_lang = db.get_selected_lang(chat_id)
        prev_lang = current_lang

        cursor.execute('''UPDATE users SET selected_price = ?, selected_voucher = ?,
                                           selected_lang = ?, previous_lang = ?, user_selected_voucher = ?,
                                            dark_soul_code = ? WHERE chat_id = ?''',
                       (None, None, selected_lang, prev_lang, None, None, chat_id))

    conn.commit()
    conn.close()
    await data_controller(update, context)


async def data_controller(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Data Controller Function Description

    The `data_controller` function manages the flow of data processing and response generation based on user
    interactions in a Telegram bot application. It orchestrates actions such as retrieving or deleting data from the
    database, handling user-selected options, and navigating between different functionalities.

    Functionality:

    - Retrieves essential data from the database, including selected language, FAQ option, selected function,
    selected voucher, and selected price. - Determines the appropriate action based on the retrieved data,
    such as displaying FAQ information, executing selected functions, managing voucher-related actions, or handling
    language changes. - Generates dynamic responses tailored to user interactions, including sending messages,
    photos, or inline keyboard options. - Utilizes inline keyboards to provide users with interactive options,
    such as navigating back to the main menu or accessing specific functionalities. - Deletes unnecessary data from
    the database after processing user requests to ensure data cleanliness and optimize performance. - Ensures
    consistency in language selection by redirecting users to the main menu if the selected language changes.

    Usage:

    - This function is designed to be integrated into the main logic of a Telegram bot application, serving as a
    central controller for processing user interactions and managing data flow. - It facilitates seamless
    communication between users and the bot by dynamically responding to user actions and providing relevant
    information or functionalities. - The function enhances user experience by handling various scenarios
    intelligently and guiding users through different features or options available in the bot.

    Note: Ensure that the necessary dependencies, such as database access functions and command execution logic,
    are properly implemented and accessible within the function.

    Feel free to integrate and adapt this function to suit the specific requirements of your Telegram bot
    application!"""

    chat_id = update.effective_chat.id
    message_id = update.effective_message.message_id

    # GET OR DELETE DATA IN DB
    lang = db.get_selected_lang(chat_id)
    prev_lang = db.get_prev_lang(chat_id)
    price = db.get_selected_value(chat_id)
    user_data = db.get_faq_option(chat_id)
    selected_function = db.get_selected_func(chat_id)
    func = data_to_chat.get(selected_function)
    selected_voucher = db.get_selected_voucher(chat_id)
    user_selected_voucher = db.get_user_selected_voucher(chat_id)
    clear_unnecessary_data = db.clear_unnecessary_data_from_db(chat_id)

    all_commands_button = InlineKeyboardButton(data_to_chat[lang]['main_menu_btn'], callback_data='all_commands')
    keyboard = InlineKeyboardMarkup([[all_commands_button]])

    if user_data is not None and lang is not None:
        button_text = data_to_chat[lang][user_data + '_button']
        info_button = InlineKeyboardButton(button_text, url=data_to_chat[lang][user_data])
        back_button = InlineKeyboardButton('<<< BACK', callback_data='faq')
        info = InlineKeyboardMarkup([[info_button], [back_button]])

        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        await delete_messages(update, context)

        await context.bot.send_photo(chat_id=chat_id,
                                     photo=data_to_chat.get(user_data),
                                     reply_markup=info)
        return clear_unnecessary_data

    elif selected_function is not None:
        await func(update, context)
        return clear_unnecessary_data

    elif selected_voucher is not None:
        await admin_commands.view_selected_active_voucher(update, context)
        return clear_unnecessary_data

    elif user_selected_voucher is not None:
        await voucher_commands.view_selected_user_active_voucher(update, context)
        return clear_unnecessary_data

    elif price is not None:
        await voucher_commands.manage_payment_or_price(update, context)
        return clear_unnecessary_data

    elif prev_lang != lang:
        await main_commands.all_commands(update, context)
        return clear_unnecessary_data

    elif prev_lang == lang:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        await context.bot.send_message(chat_id=chat_id, text=data_to_chat[lang]['same_lang'], reply_markup=keyboard)


#                   FAQ VIDEO PATH
how_care_image_path = 'bot_app/media/FAQ/FAQ-picture.jpg'
how_much_image_path = 'bot_app/media/FAQ/FAQ-picture.jpg'
how_prepare_image_path = 'bot_app/media/FAQ/FAQ-picture.jpg'

data_to_chat = {
    'RU': {
        'start': '''Привет! 👋
            Меня зовут DarkSoultattooBot 🤖
            Я виртуальный помощник тату-мастера AleksandrDarkSoul.
            Перейди в меню и ознакомься с информацией, которую мы для тебя приготовили.🔥
            Желаю татушного дня!😉''',

        'care': 'https://telegra.ph/Uhod-za-tatuirovkoj-03-12',
        'how_to': 'https://telegra.ph/Uhod-za-tatuirovkoj-03-12',
        'how_much': 'https://telegra.ph/Uhod-za-tatuirovkoj-03-12',
        'same_lang': "🫡Этот язык был уже выбран!",
        'care_button': 'Уход за тату',
        'how_to_button': 'Подготовка к снансу',
        'how_much_button': 'Формирование цены',
        'main_menu_btn': 'ГЛАВНОЕ МЕНЮ',
    },
    'ENG': {
        'start': ''' Hi! 👋
            I am DarkSoultattooBot 🤖
            A virtual assistant of tattoo artist AleksandrDarkSoul.
            Go to the menu and check out the information we have prepared for you.🔥
            Have a tattoo-filled day!😉''',

        'care': 'https://telegra.ph/Tattoo-care-03-12',
        'how_to': 'https://telegra.ph/Tattoo-care-03-12',
        'how_much': 'https://telegra.ph/Tattoo-care-03-12',
        'same_lang': "🫡This language already selected!",
        'care_button': 'Tattoo care',
        'how_to_button': 'Preparing for the session',
        'how_much_button': 'Price formation',
        'main_menu_btn': 'MAIN MENU',
    },
    'PL': {
        'start': '''Cześć! 👋
            Jestem DarkSoultattooBot 🤖
            Jestem wirtualnym asystentem tatuażysty AleksandrDarkSoul.
            Przejdź do menu i zapoznaj się z informacją, którą dla Ciebie przygotowaliśmy.🔥
            Życzę Ci tatuowanego dnia!😉 ''',

        'care': 'https://telegra.ph/Pielęgnacja-tatuaużu-03-12',
        'how_to': 'https://telegra.ph/Pielęgnacja-tatuaużu-03-12',
        'how_much': 'https://telegra.ph/Pielęgnacja-tatuaużu-03-12',
        'same_lang': "🫡Ten język jest już wybrany!",
        'care_button': 'Pielęgnacja tatuażu',
        'how_to_button': 'Przygotowanie do sesji',
        'how_much_button': 'Kształtowanie ceny',
        'main_menu_btn': 'GŁÓWNE MENU',
    },

    'care': how_care_image_path,
    'how_to': how_prepare_image_path,
    'how_much': how_much_image_path,

    'start': main_commands.start_command,
    'faq': main_commands.faq_command,
    'kontakt': main_commands.kontakt_command,
    'local': main_commands.location_command,
    'all_commands': main_commands.all_commands,

    'add_voucher': admin_commands.add_voucher,
    'statistics': admin_commands.statistics_command,
    'change': admin_commands.add_voucher,
    'check_voucher': admin_commands.view_all_active_vouchers,
    'save': admin_commands.accept_add_voucher,
    'activate': admin_commands.activate_voucher,
    'activated': admin_commands.view_selected_deactivate_voucher,
    'admin': admin_commands.admin_command,
    'db_in_chat': admin_commands.send_db_file_in_chat,

    'voucher': voucher_commands.voucher_command,
    'e_voucher': voucher_commands.price_command,
    'paper_voucher': voucher_commands.paper_voucher,
    'price_more': voucher_commands.price_more_command,
    'change_price': voucher_commands.price_command,
    'manage_price': voucher_commands.manage_payment_or_price,
    'check': voucher_commands.check_payment_intent,
    'get_in_chat': voucher_commands.get_voucher_in_chat,
    'user_vouchers': voucher_commands.user_vouchers,
    'user_active_vouchers': voucher_commands.user_active_vouchers,
    'selected_user_active_voucher': voucher_commands.view_selected_user_active_voucher,

    'cancel': cancel,
    'get_in_email': send_email_with_attachment,
}

actions = {
    'language_actions': {'RU': 'RU',
                         'ENG': 'ENG',
                         'PL': 'PL'},

    'faq_actions': {'care': 'care',
                    'how_to': 'how_to',
                    'how_much': 'how_much'},

    'price_actions': {'5': '5',
                      '300': '300',
                      '600': '600',
                      '800': '800',
                      '1000': '1000'},

    'function_actions': {
        'start': 'start',
        'faq': 'faq',
        'kontakt': 'kontakt',
        'local': 'local',
        'voucher': 'voucher',
        'e_voucher': 'e_voucher',
        'paper_voucher': 'paper_voucher',
        'price_more': 'price_more',
        'check_voucher': 'check_voucher',
        'all_commands': 'all_commands',
        'change_price': 'change_price',
        'save': 'save',
        'change': 'change',
        'cancel': 'cancel',
        'activate': 'activate',
        'activated': 'activated',
        'admin': 'admin',
        'manage_price': 'manage_price',
        'check': 'check',
        'get_in_chat': 'get_in_chat',
        'get_in_email': 'get_in_email',
        'user_vouchers': 'user_vouchers',
        'user_active_vouchers': 'user_active_vouchers',
        'user_inactive_vouchers': 'user_inactive_vouchers',
        'selected_user_active_voucher': 'selected_user_active_voucher'},

    'admin_actions': {
        'statistics': 'statistics',
        'add_voucher': 'add_voucher',
        'check_voucher': 'check_voucher',
        'db_in_chat': 'db_in_chat'}
}
