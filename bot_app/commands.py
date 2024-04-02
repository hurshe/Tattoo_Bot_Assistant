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
        await context.bot.send_message(chat_id=chat_id,
                                       text="Выберите язык     Choose your language    Wybierz język:",
                                       reply_markup=keyboard)

    @staticmethod
    async def kontakt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        message_id = update.effective_message.message_id
        lang = db.get_selected_lang(chat_id)

        instagram_button = InlineKeyboardButton("Instagram", url='https://www.instagram.com/alexandr_darksoul/')
        facebook_button = InlineKeyboardButton('Facebook', url='https://www.facebook.com/AlexINKINK/')
        back_button = InlineKeyboardButton(main_messages[lang]['back_btn'], callback_data='all_commands')

        keyboard = InlineKeyboardMarkup([[instagram_button, facebook_button], [back_button]])

        await context.bot.deleteMessage(chat_id=chat_id, message_id=message_id)
        await context.bot.send_photo(chat_id=chat_id, photo=main_messages['instagram_image'],
                                     caption=main_messages[lang]['kontakt'],
                                     reply_markup=keyboard)

    @staticmethod
    async def faq_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        message_id = update.effective_message.message_id
        lang = db.get_selected_lang(chat_id)

        language_buttons = {
            'RU': [
                ('Подготовка к сеансу', 'how_to'),
                ('Уход за тату', 'care'),
                ('От чего зависит цена', 'how_much'),
                (main_messages[lang]['back_btn'], 'all_commands')
            ],
            'ENG': [
                (' Preparation to session ', 'how_to'),
                (' How care to youre tattoo ', 'care'),
                ('Pricing', 'how_much'),
                (main_messages[lang]['back_btn'], 'all_commands')
            ],
            'PL': [
                ('Przygotowanie do sesji ', 'how_to'),
                ('Pielęgacja tatuażu ', 'care'),
                ('Cennik ', 'how_much'),
                (main_messages[lang]['back_btn'], 'all_commands')
            ]
        }

        keyboard = {}

        for lang_key, buttons in language_buttons.items():
            keyboard[lang_key] = InlineKeyboardMarkup([
                [InlineKeyboardButton(text, callback_data=callback)] for text, callback in buttons
            ])

        selected_keyboard = keyboard.get(lang)

        await context.bot.deleteMessage(chat_id=chat_id, message_id=message_id)
        await delete_messages(update, context)
        await context.bot.send_photo(chat_id=chat_id, photo=main_messages.get('faq_image'),
                                     caption=main_messages[lang].get('faq'),
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
        await context.bot.send_message(chat_id=chat_id,
                                       text=main_messages[lang]['all_commands'],
                                       reply_markup=keyboard_markup)
        return delete_prev_func

