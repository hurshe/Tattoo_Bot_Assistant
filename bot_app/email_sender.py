import os
import dotenv

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot_app.pdf_voucher_generator import e_voucher_generator_pdf
from bot_app.db_manager import DBManager
from bot_app.voucher_handler import delete_messages

dotenv.load_dotenv()
db = DBManager('tattoo_bot_telegram.db')


async def send_email_with_attachment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    send_email_with_attachment Function Description

    The `send_email_with_attachment` function is responsible for sending an email with an attachment to the user. It
    retrieves the user's email address from the database, constructs an email message with the specified subject,
    body, and attachment, and sends it using the configured SMTP server.

    Functionality:

    - Retrieve User Information: Retrieves the user's email address and preferred language from the database
    using the provided `chat_id`.
    - Construct Email Message: Constructs an email message with the specified
    subject and body text in the user's preferred language. Attaches the generated electronic voucher PDF file to the
    email.
    - SMTP Configuration: Retrieves SMTP server settings (server address, port, username, and password)
    from environment variables.
    - Send Email: Connects to the SMTP server, authenticates the sender's
    credentials, and sends the email with the attached PDF file to the user's email address.
    - Handle
    Success/Failure: If the email is successfully sent, it notifies the user in the Telegram chat. If the user does
    not have a valid email address stored, it sends a message indicating that an email address is required.

    Usage:

    - Invoke this function when the user requests to receive an electronic voucher via email with an attachment. -
    Ensure that the user's email address is stored in the database before calling this function.
    - Customize the email subject, body text, and back button text based on the user's preferred language.
    - Configure the SMTP server settings (server address, port, username, and password) as environment variables
    for secure communication.
    - Handle any errors or exceptions that may occur during the email sending process, such as invalid email
    addresses or SMTP server connection issues.

    Note: This function relies on external libraries (`smtplib`, `email.mime`, etc.) for email handling and
    attachment transmission. Ensure that these libraries are installed and accessible within your Python environment.

    Feel free to integrate and adapt this function to suit the specific requirements of your Telegram bot
    application!"""

    chat_id = update.effective_chat.id
    lang = db.get_selected_lang(chat_id)
    user_email = db.get_user_email(chat_id)
    if user_email is not None:
        subject = email_text_to_send[lang]['title']
        message = email_text_to_send[lang]['message']
        from_email = os.getenv('SMTP_USERNAME')
        to_email = user_email
        attachment_path = e_voucher_generator_pdf(chat_id)[0]
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        smtp_username = os.getenv('SMTP_USERNAME')
        smtp_password = os.getenv('SMTP_PASSWORD')

        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(message, 'plain'))

        with open(attachment_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename= {attachment_path}")
        msg.attach(part)

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()

        back_button = InlineKeyboardButton(email_text_to_send[lang]['back_btn'],
                                           callback_data='selected_user_active_voucher')
        keyboard = InlineKeyboardMarkup([[back_button]])

        await delete_messages(update, context)
        await context.bot.send_message(chat_id=chat_id, text=email_text_to_send[lang]['chat_message'],
                                       reply_markup=keyboard)
    else:
        await context.bot.send_message(chat_id=chat_id, text=email_text_to_send[lang]['invalid_email'])

email_text_to_send = {
    'RU': {
        'title': 'DarkSoulVoucher',
        'message': "Здравствуйте,\n\n"

                   "Поздравляю с приобретением ваучера у тату-мастера Александра DarkSoul.🥳\n\n"

                   "Для использования ваучера, пожалуйста, предоставьте код тату-мастеру.\n\n"

                   "ВАЖНО ПОМНИТЬ❗\n\n"

                   "❌ Не демонстрируйте ваш личный код третьим лицам.\n"
                   "❌ Не публикуйте ваш код в социальных сетях.\n\n"
                   
                   "Если кто-то воспользуется вашим кодом, мы не несем за это ответственности. Если вы хотите "
                   "подарить ваучер третьему лицу, обязательно передайте высше указаную информацию\n"

                   "Спасибо за покупку, и желаю вам прекрасного татушного дня! 🖤\n\n"

                   "DarkSoulAssistant",
        'chat_message': "Ваучер успешно отправлен на вашу почту!\n"
                        "Проверьте папку 'СПАМ', если не найдете сообщения во входящих.\n"
                        "Спасибо за покупку! 🖤",
        'invalid_email': "Ваучер был продан в бумажной версии, у меня нет доступа к электронной почте,"
                         " на которую вы хотите получить ваучер!",
        'back_btn': '⏪ Назад'
    },
    'ENG': {
        'title': 'DarkSoulVoucher',
        'message': "Hello,\n\n"

                   "Congratulations on purchasing a voucher from tattoo master Alexander DarkSoul. 🥳\n\n"

                   "To use the voucher, please provide the code to the tattoo master.\n\n"

                   "IMPORTANT REMINDERS❗\n\n"

                   "❌ Do not disclose your personal code to third parties.\n"
                   "❌ Do not publish your code on social media platforms.\n\n"
                   
                   "If someone uses your code, we do not take responsibility for it.\n"
                   "If you want to give the voucher to a third party, "
                   "make sure to pass on the above information\n"

                   "Thank you for your purchase, and I wish you a wonderful tattoo-filled day! 🖤\n\n"

                   "DarkSoulAssistant",
        'chat_message': "Your voucher has been successfully sent to your email!\n"
                        "Check your SPAM folder if you don't find the message in your inbox.\n"
                        "Thank you for your purchase! 🖤",
        'invalid_email': "The voucher was sold in paper format, I don't have access to the email you want to receive "
                         "the voucher on! ",
        'back_btn': '⏪ BACK'
    },
    'PL': {
        'title': 'DarkSoulVoucher',
        'message':
            "Witaj,\n\n"

            "Gratuluję zakupu vouchera u mistrza tatuażu Aleksandra DarkSoul. 🥳\n\n"

            "Aby skorzystać z vouchera, proszę podać kod mistrzowi tatuażu.\n\n"

            "WAZNE PRZYPOMNIENIA❗\n\n"

            "❌ Nie udostępniaj swojego osobistego kodu osobom trzecim.\n"
            "❌ Nie publikuj swojego kodu w mediach społecznościowych.\n\n"
            
            "Jeśli ktoś użyje Twojego kodu, nie ponosimy za to odpowiedzialności.\n"
            "Jeśli chcesz podarować voucher osobie trzeciej, upewnij się, że przekazujesz powyższe informacje\n"

            "Dziękuję za zakup i życzę Ci wspaniałego dnia pełnego tatuaży! 🖤\n\n"

            "DarkSoulAssistant",
        'chat_message': "Twój voucher został pomyślnie wysłany na twój adres e-mail!\n"
                        "Sprawdź folder SPAM, jeśli nie znajdziesz wiadomości w skrzynce odbiorczej.\n"
                        "Dziękujemy za zakup! 🖤",
        'invalid_email': "Voucher został sprzedany w formie papierowej, nie mam dostępu do e-maila, na który chcesz "
                         "otrzymać voucher! ",
        'back_btn': '⏪ Wstecz'

    }

}
