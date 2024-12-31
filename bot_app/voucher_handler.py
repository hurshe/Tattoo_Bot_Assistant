import os
import secrets
import string

import dotenv
import stripe

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot_app.db_manager import DBManager
from bot_app.pdf_voucher_generator import e_voucher_generator_pdf
from bot_app.chat_actions import delete_messages, voucher_messages

dotenv.load_dotenv()

STRIPE_API_KEY = os.getenv('STRIPE_API_KEY')
stripe.api_key = STRIPE_API_KEY

db = DBManager('tattoo_bot_telegram.db')


def check_payment_data(chat_id):
    """
    check_payment_data Function Description

    The `check_payment_data` function verifies payment data for completed checkout sessions using the Stripe API. It
    retrieves payment events of type "checkout.session.completed" from the Stripe API and iterates through each event
    to identify successful payments matching the specified criteria.

    Functionality:

    - Retrieve Payment Events: Retrieves payment events of type "checkout.session.completed" from the Stripe API
    using the `stripe.Event.list` method. The function iterates through the paginated list of events using
    `auto_paging_iter`.

    - Verify Payment Status: For each payment event, extracts the session data and checks the payment status. If
    the payment status is "paid," proceeds with further verification.

    - Check Dark Soul Code: Retrieves the Dark Soul code associated with the user's chat ID from the database.
    Compares the Dark Soul code provided during the payment session with the Dark Soul code stored in the database.

    - Process Valid Payment: If the Dark Soul code matches and the payment status is "paid," retrieves additional
    payment details such as the payment value and customer email address. Stores the customer email address in the
    database.

    - Return Payment Data: Returns the customer email address, Dark Soul code, payment status (True for success),
    payment value, and database update status.

    Usage:

    - Invoke this function to verify payment data for completed checkout sessions processed through the Stripe API.
    - Ensure that the function is triggered periodically or in response to specific events to keep payment data
    up-to-date.
    - Customize the payment verification criteria based on your application's requirements,
    such as additional fields or validation checks.
    - Handle any errors or exceptions that may occur during the
    payment verification process, such as network issues or invalid data.

    Note: This function relies on the Stripe API for retrieving payment events and requires proper configuration
    and authentication with your Stripe account. Ensure that your Stripe API keys are securely stored and managed.

    Feel free to integrate and adapt this function to suit the specific payment processing needs of your application!"""

    payment_events = stripe.Event.list(type="checkout.session.completed")

    for event in payment_events.auto_paging_iter():
        dk_code_db = db.get_dark_soul_code(chat_id)
        session = event.data.object
        payment_status = session.payment_status

        if payment_status == "paid":
            if session.custom_fields:
                dark_soul_code = session.custom_fields[0].text.get("value", "")
                if dark_soul_code == dk_code_db:
                    payment_value = session.amount_total
                    payment_email = session.customer_details.email
                    add_email_db = db.add_user_email_in_db(chat_id, payment_email)

                    return payment_email, dark_soul_code, True, payment_value, add_email_db
        break


class VoucherCommands:
    """
    This class provides methods to handle various voucher-related commands in a Telegram bot.

    Methods: - voucher_command(update: Update, context: ContextTypes.DEFAULT_TYPE): Displays options for vouchers.
    - price_command(update: Update, context: ContextTypes.DEFAULT_TYPE): Displays price options for vouchers.
    - price_more_command(update: Update, context: ContextTypes.DEFAULT_TYPE): Provides additional information about
    voucher prices.
    - manage_payment_or_price(update: Update, context: ContextTypes.DEFAULT_TYPE): Manages payment
    actions and voucher prices.
    - paper_voucher(update: Update, context: ContextTypes.DEFAULT_TYPE): Displays options
    for paper vouchers.
    - check_payment_intent(update: Update, context: ContextTypes.DEFAULT_TYPE): Checks the status
    of payment intent.
    - get_voucher_in_chat(update: Update, context: ContextTypes.DEFAULT_TYPE): Sends a voucher to
    the user via chat.
    - user_vouchers(update: Update, context: ContextTypes.DEFAULT_TYPE): Displays a user's
    vouchers.
    - user_active_vouchers(update: Update, context: ContextTypes.DEFAULT_TYPE): Displays active vouchers
    for the user.
    - view_selected_user_active_voucher(update: Update, context: ContextTypes.DEFAULT_TYPE): Views
    selected active vouchers for the user.
    """

    @staticmethod
    async def voucher_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        lang = db.get_selected_lang(chat_id)

        e_voucher_button = InlineKeyboardButton('E-VOUCHER', callback_data='e_voucher')
        paper_voucher_button = InlineKeyboardButton('P-VOUCHER', callback_data='paper_voucher')
        user_vouchers_button = InlineKeyboardButton('MY VOUCHERS', callback_data='user_vouchers')
        back_button = InlineKeyboardButton(voucher_messages[lang]['back_btn'], callback_data='all_commands')

        keyboard = InlineKeyboardMarkup(
            [
                [e_voucher_button, paper_voucher_button],
                [user_vouchers_button],
                [back_button]
            ])

        await delete_messages(update, context)
        with open('bot_app/media/Voucher/main_voucher_img.PNG', 'rb') as image_file:
            await context.bot.send_photo(chat_id=chat_id, photo=image_file,
                                         caption=voucher_messages[lang]['voucher'], reply_markup=keyboard)

    @staticmethod
    async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        lang = db.get_selected_lang(chat_id)

        button_300 = InlineKeyboardButton('300 PLN', callback_data='300')
        button_600 = InlineKeyboardButton('600 PLN', callback_data='600')
        button_800 = InlineKeyboardButton('800 PLN', callback_data='800')
        button_1000 = InlineKeyboardButton('1000 PLN', callback_data='1000')
        more_button = InlineKeyboardButton('🤑1000+🤑', callback_data='price_more')
        back_button = InlineKeyboardButton(voucher_messages[lang]['back_btn'], callback_data='voucher')

        keyboard = InlineKeyboardMarkup(
            [
                [button_300, button_600],
                [button_800, button_1000],
                [more_button],
                [back_button]
            ])

        await delete_messages(update, context)
        with open('bot_app/media/money.jpg', 'rb') as image_file:
            await context.bot.send_photo(chat_id=chat_id, photo=image_file,
                                         caption=voucher_messages[lang]['price_info'], reply_markup=keyboard)

    @staticmethod
    async def price_more_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        lang = db.get_selected_lang(chat_id)

        instagram_keyboard = InlineKeyboardButton("Instagram", url='https://www.instagram.com/alexsun_darksoul/')
        linkedin_keyboard = InlineKeyboardButton('Facebook',
                                                 url='https://www.facebook.com/profile.php?id=100089965814206')
        back_button = InlineKeyboardButton(voucher_messages[lang]['back_btn'], callback_data='change_price')

        keyboard = InlineKeyboardMarkup([[instagram_keyboard, linkedin_keyboard], [back_button]])

        await delete_messages(update, context)
        with open('bot_app/media/more_image.JPG', 'rb') as image_file:
            await context.bot.send_photo(chat_id=chat_id, photo=image_file,
                                         caption=voucher_messages[lang]['price_more_info'], reply_markup=keyboard)

    @staticmethod
    async def manage_payment_or_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        selected_value = str(db.get_selected_value(chat_id))
        lang = db.get_selected_lang(chat_id)

        randomizer = string.ascii_uppercase + string.digits
        dark_soul_code = ''.join(secrets.choice(randomizer) for i in range(5))
        db.add_dark_soul_code(dark_soul_code, chat_id)

        payment_actions = {
            '300': 'https://t.me/tattoo_assistant_bot/payment_300_pln',
            '600': 'https://t.me/tattoo_assistant_bot/payment_600_pln',
            '800': 'https://t.me/tattoo_assistant_bot/payment_800_pln',
            '1000': 'https://t.me/tattoo_assistant_bot/payment_1000_pln',
            'RU': {
                'pay': 'Заплатить',
                'change': 'Изменить цену',
                'check': 'Проверить платеж'
            },
            'PL': {
                'pay': 'Zapłać',
                'change': 'Zmień cenę',
                'check': 'Sprawdź płatność'
            },
            'ENG': {
                'pay': 'PAY',
                'change': 'Change price',
                'check': 'Check Payment'
            }
        }

        if selected_value in payment_actions:
            url = payment_actions[selected_value]
            button_pay = InlineKeyboardButton(payment_actions[lang]['pay'], url=url)
            button_change_price = InlineKeyboardButton(payment_actions[lang]['change'], callback_data='change_price')
            check_payment = InlineKeyboardButton(payment_actions[lang]['check'], callback_data='check')
            back_button = InlineKeyboardButton(voucher_messages[lang]['back_btn'], callback_data='change_price')

            keyboard = InlineKeyboardMarkup([[button_pay, button_change_price], [check_payment], [back_button]])

            await delete_messages(update, context)
            with open('bot_app/media/payment_img.PNG', 'rb') as image_file:
                await context.bot.send_photo(chat_id=chat_id, photo=image_file,
                                             caption=voucher_messages[lang]['payment'] % (
                                             selected_value, dark_soul_code),
                                             reply_markup=keyboard)
        else:
            pass

    @staticmethod
    async def paper_voucher(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        lang = db.get_selected_lang(chat_id)

        inst_button = InlineKeyboardButton('Instagram', url='https://www.instagram.com/alexsun_darksoul/')
        facebook_button = InlineKeyboardButton('Facebook',
                                               url='https://www.facebook.com/profile.php?id=100089965814206')
        back_button = InlineKeyboardButton(voucher_messages[lang]['back_btn'], callback_data='voucher')

        keyboard = InlineKeyboardMarkup([[inst_button, facebook_button], [back_button]])

        await delete_messages(update, context)
        with open('bot_app/media/Voucher/paper_voucher_image.PNG', 'rb') as image_file:
            await context.bot.send_photo(chat_id=chat_id, photo=image_file,
                                         caption=voucher_messages[lang]['paper_voucher'], reply_markup=keyboard)

    @staticmethod
    async def check_payment_intent(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        lang = db.get_selected_lang(chat_id)

        code = string.ascii_uppercase + string.ascii_lowercase + string.digits
        serial_number = ''.join(secrets.choice(code) for i in range(10))

        user_vouchers_button = InlineKeyboardButton(voucher_messages[lang]['my_vouchers_btn'],
                                                    callback_data='user_vouchers')
        main_menu_button = InlineKeyboardButton(voucher_messages[lang]['main_menu_btn'], callback_data='all_commands')

        keyboard = InlineKeyboardMarkup([[user_vouchers_button], [main_menu_button]])

        payment_data = check_payment_data(chat_id)
        voucher_code = serial_number

        if payment_data is not None:
            voucher_value = payment_data[3] // 100

            if True in payment_data:
                db.add_voucher_by_payment(chat_id, voucher_code, voucher_value)

                await delete_messages(update, context)
                await context.bot.send_message(chat_id=chat_id,
                                               text=voucher_messages[lang]['successful_payment'] % (
                                                   voucher_value, payment_data[1], payment_data[0]),
                                               reply_markup=keyboard)
        else:
            await context.bot.send_message(chat_id=chat_id, text=voucher_messages[lang]['invalid_payment'])

    @staticmethod
    async def get_voucher_in_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        lang = db.get_selected_lang(chat_id)

        back_button = InlineKeyboardButton(voucher_messages[lang]['back_btn'],
                                           callback_data='selected_user_active_voucher')
        keyboard = InlineKeyboardMarkup([[back_button]])

        await delete_messages(update, context)
        await context.bot.send_message(chat_id=chat_id, text=voucher_messages[lang]['voucher_in_chat'],
                                       reply_markup=keyboard)
        await context.bot.send_document(chat_id=chat_id, document=e_voucher_generator_pdf(chat_id)[0])

    @staticmethod
    async def user_vouchers(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        lang = db.get_selected_lang(chat_id)

        active_vouchers_button = InlineKeyboardButton('ACTIVE VOUCHERS', callback_data='user_active_vouchers')
        back_button = InlineKeyboardButton(voucher_messages[lang]['back_btn'], callback_data='voucher')

        keyboard = InlineKeyboardMarkup([[active_vouchers_button], [back_button]])

        await delete_messages(update, context)
        with open('bot_app/media/Voucher/my_vouchers_img.PNG', 'rb') as image_file:
            await context.bot.send_photo(chat_id=chat_id,
                                         photo=image_file,
                                         caption=voucher_messages[lang]['user_vouchers'],
                                         reply_markup=keyboard)

    @staticmethod
    async def user_active_vouchers(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        lang = db.get_selected_lang(chat_id)
        user_vouchers_in_db = db.get_vouchers_by_user(chat_id)

        buttons = {f'{item[0]} - {item[2]} PLN': f'{item[0]}-{chat_id}' for item in user_vouchers_in_db}
        buttons[voucher_messages[lang]['back_btn']] = "user_vouchers"
        buttons_per_row = 3

        keyboard_buttons = [
            [
                InlineKeyboardButton(button_text, callback_data=callback_data)
                for button_text, callback_data in buttons.items()
            ][i:i + buttons_per_row]
            for i in range(0, len(buttons), buttons_per_row)
        ]

        keyboard = InlineKeyboardMarkup(keyboard_buttons)

        await delete_messages(update, context)
        if user_vouchers_in_db:
            await context.bot.send_message(chat_id=chat_id,
                                           text=voucher_messages[lang]['active_vouchers'],
                                           reply_markup=keyboard)
        else:
            await context.bot.send_message(chat_id=chat_id,
                                           text=voucher_messages[lang]['active_vouchers_empty'],
                                           reply_markup=keyboard)

    @staticmethod
    async def view_selected_user_active_voucher(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        lang = db.get_selected_lang(chat_id)
        user_selected_voucher = db.get_user_selected_voucher(chat_id)
        selected_voucher = user_selected_voucher.split("-")[0]
        price_of_selected_voucher = db.get_price_voucher(chat_id, selected_voucher)

        get_in_chat_button = InlineKeyboardButton('GET IN CHAT', callback_data='get_in_chat')
        get_in_email_button = InlineKeyboardButton('GET IN EMAIL', callback_data='get_in_email')
        back_button = InlineKeyboardButton(voucher_messages[lang]['back_btn'], callback_data='user_vouchers')

        keyboard = InlineKeyboardMarkup([[get_in_chat_button, get_in_email_button], [back_button]])

        await delete_messages(update, context)
        await context.bot.send_message(chat_id=chat_id,
                                       text=(voucher_messages[lang]['user_selected_voucher']) % (
                                           selected_voucher, price_of_selected_voucher),
                                       reply_markup=keyboard)
