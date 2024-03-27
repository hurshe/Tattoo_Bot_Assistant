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

