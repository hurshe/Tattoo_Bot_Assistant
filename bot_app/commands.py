import os

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot_app.db_manager import DBManager
from bot_app.chat_actions import main_messages, delete_messages

load_dotenv()
admin_chat_id = os.getenv('admin_id')
sub_admin_id = os.getenv('sub_admin_id')
db = DBManager('tattoo_bot_telegram.db')


class MainMenuCommands:
    """
    MainMenuCommands Class Description

    The `MainMenuCommands` class comprises a collection of static methods responsible for handling various commands
    within a Telegram bot's main menu. These methods facilitate user interaction by offering functionalities such as
    selecting language preferences, accessing frequently asked questions (FAQs), viewing contact information,
    and obtaining location details.

    Static Methods:

    1. `start_command(update: Update, context: ContextTypes.DEFAULT_TYPE)`
       - Initiates the bot's interaction with the user by presenting language options.
       - Allows users to select their preferred language.

    2. `kontakt_command(update: Update, context: ContextTypes.DEFAULT_TYPE)`
       - Displays contact information, including Instagram and Facebook links.
       - Allows users to return to the main menu.
    3. `faq_command(update: Update, context: ContextTypes.DEFAULT_TYPE)`
       - Provides access to frequently asked questions (FAQs) categorized by language.
       - Enables users to navigate through different FAQ topics and return to the main menu.

    4. `location_command(update: Update, context: ContextTypes.DEFAULT_TYPE)`
       - Shares the bot's location with users, typically representing the bot's physical business location.
       - Allows users to view the location and return to the main menu.

    5. `all_commands(update: Update, context: ContextTypes.DEFAULT_TYPE)` - Displays all available commands in
    the main menu. - Enables users to select various options such as starting the bot, accessing FAQs, contacting the
    bot owner, viewing location details, or accessing voucher-related functionalities.

    Usage: - These static methods are designed to be integrated into a Telegram bot application's main menu
    functionality, providing users with convenient access to essential features and information. - Each method serves
    a specific purpose within the main menu interface, allowing users to navigate through different options
    seamlessly. - The class ensures an organized and user-friendly experience for interacting with the bot's main menu.

    Note: Ensure that the bot has the necessary permissions to delete messages and interact with inline keyboards
    in the chat where it operates.

    """

    @staticmethod
    async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        message_text = update.effective_message.text

        russian_button = InlineKeyboardButton('🇺🇦 RU', callback_data='RU')
        english_button = InlineKeyboardButton('🇺🇲 ENG', callback_data="ENG")
        polish_button = InlineKeyboardButton('🇵🇱 PL', callback_data='PL')

        keyboard = InlineKeyboardMarkup([[russian_button, english_button, polish_button]])
        try:
            if message_text != '/start':
                await delete_messages(update, context)
        except Exception as e:
            return e
        with open('bot_app/media/start_img.PNG', 'rb') as image_file:
            await context.bot.send_photo(chat_id=chat_id, photo=image_file, reply_markup=keyboard)

    @staticmethod
    async def kontakt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        message_id = update.effective_message.message_id
        lang = db.get_selected_lang(chat_id)

        instagram_button = InlineKeyboardButton("INSTAGRAM", url='https://www.instagram.com/alexsun_darksoul/')
        facebook_button = InlineKeyboardButton('FACEBOOK', url='https://www.facebook.com/profile.php?id=100089965814206')
        back_button = InlineKeyboardButton(main_messages[lang]['back_btn'], callback_data='all_commands')

        keyboard = InlineKeyboardMarkup([[instagram_button, facebook_button], [back_button]])

        await context.bot.deleteMessage(chat_id=chat_id, message_id=message_id)
        with open('bot_app/media/instagram.PNG', 'rb') as image_file:
            await context.bot.send_photo(chat_id=chat_id, photo=image_file,
                                         caption=main_messages[lang]['kontakt'],
                                         reply_markup=keyboard)

    @staticmethod
    async def faq_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        message_id = update.effective_message.message_id
        lang = db.get_selected_lang(chat_id)

        language_buttons = {
            'RU': [
                ('♻️ Подготовка к сеансу', 'https://telegra.ph/Podgotovka-k-seansu-11-05'),
                ('✅ Правильный уход за тату', 'https://telegra.ph/Uhod-za-tatuirovkoj-11-04'),
                ('💸 Формирование цены', 'https://telegra.ph/Cenoobrazovanie-tatuirovok-10-29'),
                ('🧾 Для чего нужна консультация', 'https://telegra.ph/Konsultaciya-11-15-2'),
                (main_messages[lang]['back_btn'], 'all_commands')
            ],
            'ENG': [
                ('♻️ Tattoo Session Prep Guide', 'https://telegra.ph/Preparing-for-the-Session-11-26-6'),
                ('✅ Tattoo Aftercare Guide', 'https://telegra.ph/Tattoo-Aftercare-Guide-11-26-2'),
                ('💸 Tattoo Pricing Guide', 'https://telegra.ph/Tattoo-Pricing-Guide-11-26-6'),
                ('🧾 Tattoo Consultation Overview', 'https://telegra.ph/Tattoo-Consultation-Overview-11-26'),
                (main_messages[lang]['back_btn'], 'all_commands')
            ],
            'PL': [
                ('♻️ Przygotowanie do sesji tatuażu', 'https://telegra.ph/Przygotowanie-przed-sesją-11-28-6'),
                ('✅ Pielęgnacja Tatuażu', 'https://telegra.ph/Pielęgnacja-tatuażu-12-01-2'),
                ('💸 Formowanie ceny na tatuaże', 'https://telegra.ph/Formowanie-ceny-na-tatuaże-12-01-5'),
                ('🧾 Cel i Zakres Konsultacji', 'https://telegra.ph/Cel-i-Zakres-Konsultacji-12-01-3'),
                (main_messages[lang]['back_btn'], 'all_commands')
            ]
        }

        keyboard = {}

        for lang_key, buttons in language_buttons.items():
            keyboard[lang_key] = InlineKeyboardMarkup([
                [InlineKeyboardButton(text, url=url if 'http' in url else None,
                                      callback_data=url if 'http' not in url else None)]
                for text, url in buttons
            ])

        selected_keyboard = keyboard.get(lang)

        await context.bot.deleteMessage(chat_id=chat_id, message_id=message_id)
        await delete_messages(update, context)
        with open('bot_app/media/FAQ/main_faq.PNG', 'rb') as image_file:
            await context.bot.send_photo(chat_id=chat_id, photo=image_file,
                                         reply_markup=selected_keyboard)

    @staticmethod
    async def location_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        lang = db.get_selected_lang(chat_id)

        latitude, longitude = 52.234496916779186, 21.0165569344955

        back_button = InlineKeyboardButton(main_messages[lang]['back_btn'], callback_data='all_commands')
        info_btn = InlineKeyboardButton(main_messages[lang]['localization'], callback_data='local')

        keyboard = InlineKeyboardMarkup([[info_btn], [back_button]])

        await delete_messages(update, context)
        await context.bot.send_location(chat_id=chat_id, latitude=latitude,
                                        longitude=longitude, reply_markup=keyboard, )

    @staticmethod
    async def all_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        message_id = update.effective_message.message_id
        lang = db.get_selected_lang(chat_id)
        message_text = update.effective_message.text
        delete_prev_func = db.delete_prev_func_from_db(chat_id)

        buttons_info = {
            'START': 'start',
            'F.A.Q': 'faq',
            'KONTAKT': 'kontakt',
            'LOCALIZATION': 'local',
            'VOUCHER': 'voucher'
        }

        buttons_per_row = 2

        keyboard_buttons = [
            [
                InlineKeyboardButton(button_text, callback_data=callback_data)
                for button_text, callback_data in buttons_info.items()
            ][i:i + buttons_per_row]
            for i in range(0, len(buttons_info), buttons_per_row)
        ]

        keyboard_markup = InlineKeyboardMarkup(keyboard_buttons)

        try:
            if message_text == '/start':
                await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            else:
                await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
                await delete_messages(update, context)
        except Exception as e:
            return e
        with open('bot_app/media/main_menu_img.PNG', 'rb') as image_file:
            await context.bot.send_photo(chat_id=chat_id,
                                         photo=image_file,
                                         reply_markup=keyboard_markup)

        return delete_prev_func

