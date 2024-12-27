from telegram import Update
from telegram.ext import ContextTypes

from bot_app.db_manager import DBManager

db = DBManager('tattoo_bot_telegram.db')


async def delete_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Delete Messages Function

    The `delete_messages` function is an asynchronous function designed to delete specific messages in a Telegram
    chat. It takes two parameters: `update` and `context`, which are objects containing information about the
    incoming update and the bot's context, respectively.

    Parameters: - `update`: An object containing information about the incoming update, such as the chat ID and
    message ID. - `context`: An object providing the context for the bot's execution, including access to the
    Telegram Bot API methods.

    Functionality: 1. Retrieves the `chat_id` and `message_id` from the `update` object, representing the ID of
    the chat and the ID of the message to be deleted, respectively. 2. Retrieves the `first_message_id` from the
    database for the given `chat_id`, which indicates the ID of the first message in the chat. 3. Iterates over a
    range from 1 to 10 to delete messages around the `message_id`. 4. Attempts to delete messages preceding and
    succeeding the `message_id` by a certain offset (up to 10 messages in both directions). 5. Checks if the message
    to be deleted is not the first message in the chat (`message_id != first_message_id`) before attempting deletion.
    6. If an exception occurs during deletion, it is caught and returned.

    Usage: - This function can be used within a Telegram bot application to delete specific messages in a chat,
    typically used for cleaning up previous bot interactions or managing message clutter. - It can be integrated into
    administrative commands or message processing logic to provide a streamlined user experience and maintain chat
    cleanliness.

    Note: Ensure that the bot has the necessary permissions to delete messages in the chat where it operates.

    """
    chat_id = update.effective_chat.id
    message_id = update.effective_message.message_id
    first_message_id = db.get_message_id(chat_id)

    for i in range(1, 10):
        try:
            if message_id - i != first_message_id:
                await context.bot.deleteMessage(chat_id=chat_id, message_id=message_id)
                await context.bot.delete_message(chat_id=chat_id, message_id=message_id - i)
            else:
                break
        except Exception as e:
            return e

    for i in range(1, 10):
        try:
            if message_id + i != first_message_id:
                await context.bot.deleteMessage(chat_id=chat_id, message_id=message_id)
                await context.bot.delete_message(chat_id=chat_id, message_id=message_id + i)
            else:
                break
        except Exception as e:
            return e


main_messages = {
    'RU': {
        'kontakt': "_______‍ПОДПИСЫВАЙСЯ________"
                   "📱  Будь в курсе всех событий  📱",
        'localization': "📍Wojciecha Górskiego 4, Warszawa",
        'back_btn': '⏪ Назад'
    },
    'ENG': {
        'kontakt': "__________SUBSCRIBE__________"
                   "📱Stay informed about all events📱",
        'localization': "📍Wojciecha Górskiego 4, Warszawa",
        'back_btn': '⏪ Back'
    },
    'PL': {
        'kontakt': "________SUBSKRYBUJ_________"
                   "📱      Aktualności na bieżąco      📱",
        'localization': "📍Wojciecha Górskiego 4, Warszawa",
        'back_btn': '⏪ Wstecz'
    },

    'admin_info': 'Нажми на "CHECK VOUCHER" что бы проверить ваучер клиента!',
}

voucher_messages = {
    'RU': {
        'voucher': "🎁 E-Voucher:\n"
                   "Это электронный ваучер, доступный для приобретения прямо через телеграм-бота.\n\n"
                   "🎁 Paper Voucher:\n"
                   "В данном разделе вы узнаете, как получить бумажный ваучер.\n\n"
                   "✅ MY VOUCHERS:\n"
                   "В этом разделе вы найдете все приобретенные вами электронные ваучеры,"
                   " доступные непосредственно в телеграм-боте.\n\n"
                   "❗ВАЖНО:\n"
                   "В MY VOUCHERS не отображаются бумажные ваучеры, приобретенные у тату-мастера.",
        'price_info': "😍 Выберите на какю сумму должен быть ваучер\n"
                      "❗Цена в польских злотых (PLN)",
        'price_more_info': "Если ваучер превишает сумму 1000 PLN, вам нужно связаться с мастером!\n"
                           "Вот его контакты📱:",
        'paper_voucher': "🎁Бумажный ваучер от мастера — это не только возможность получить качественную услугу, но и уникальный сувенир на память.\n\n"
                         "Бумажный ваучер станет отличным подарком для близких, даря незабываемые эмоции и профессиональный подход. \n\n"
                         "Чтобы приобрести ваучер, свяжитесь с мастером!\nКонтакты📱:",
        'payment': "Вы выбрали %s PLN.\n\n"
                   "✅Для оплаты, нажмите [PAY]\n"
                   "🔁Изменить цену, нажмите [CHANGE "
                   "PRICE]\n\n"
                   "Ваш DarkSoulCode для потверждения оплаты:\n\n"
                   "🔴 %s 🔴\n\n"
                   "Введите его при оплате в поле DarkSoulCode❗\n",

        'description_of_voucher': "Этот ваучер предназначен для оплаты услуги тату у мастера Aleksandr DarkSoul.\n"
                                  "Данный ваучер нельзя:\n\n"
                                  "❌ - Обналичить\n"
                                  "❌ - Поменять\n"
                                  "❌ - Вернуть\n\n"
                                  "Для более детальной информации свяжитесь с мастером!\n",
        'buttons_under_payment': "[PAY] - Перейти к оплате\n"
                                 "[CHANGE PRICE] - Изменить сумму ваучера\n"
                                 "[CHECK PAYMENT] - Подтвердить платеж\n",
        'voucher_in_chat': "Поздравляю с приобретением ваучера у тату-мастера Александра DarkSoul.🥳\n\n"

                           "Для использования ваучера, пожалуйста, предоставьте код тату-мастеру.\n\n"

                           "ВАЖНО ПОМНИТЬ❗\n\n"

                           "❌ - Не демонстрируйте ваш личный код третьим лицам.\n"
                           "❌ - Не публикуйте ваш код в социальных сетях.\n\n"

                           "Если кто-то воспользуется вашим кодом, мы не несем за это ответственности. Если вы хотите "
                           "подарить ваучер третьему лицу, обязательно передайте высше указаную информацию\n\n"

                           "Спасибо за покупку, и желаю вам прекрасного татушного дня! 🖤\n\n"

                           "DarkSoulAssistant",
        'invalid_payment':
            "Оплата не была совершена или была неудачной 😥\n"
            "Если вы совершили оплату, но не получили ваучер,"
            "пожалуйста, напишите нам на адрес электронной почты: dark.soul.assistant@gmail.com\n\n"
            "🚨Мы свяжемся с вами как можно скорее🚨",
        'user_vouchers': 'В [ACTIVE VOUCHERS] храняться ваши активные ваучеры\n\n'
                         'Ваучер можно:\n\n'
                         '📥 - Скачать\n'
                         '📭 - Получить на почту\n'
                         '👀 - Перодоставить мастеру\n\n'
                         'ВАЖНО❗\n'
                         '(Если ваучер был использован он приходит в негодность и не будет отображаться '
                         'в этом разделе)\n\n'
                         'Благодарю вас за использрвание нашего сервиса🖤',
        'successful_payment': "Оплата прошла успешно ✅\n"
                              "- Сумма: %s \n"
                              "- DarkSoulCode: %s \n"
                              "- Email: %s",
        'active_vouchers': '✅Выберите какой ваучер вы хотите получить:',
        'active_vouchers_empty': '❌К сожалению, пока здесь нет купленных ваучеров.\n'
                                 '- Чтобы купить ваучер, перейдите в меню и выберите E-Voucher, чтобы приобрести '
                                 'электронную версию ваучера.',
        'user_selected_voucher': f"✅Вы выбрали ваучер:\n\n"
                                 f"- ID:  %s \n"
                                 f"- Цена: %s PLN\n\n"
                                 f"📥 Выберите [GET IN CHAT], чтобы получить ваучер в чате.\n"
                                 f"📭 Выберите [GET IN EMAIL], чтобы получить ваучер на почту, указанную вами при "
                                 f"оплате.\n",
        'back_btn': '⏪ Назад',
        'main_menu_btn': '⏪ ГЛАВНОЕ МЕНЮ',
        'my_vouchers_btn': '⏩ Мои ваучеры'
    },
    'ENG': {
        'voucher': "🎁 E-Voucher:\n"
                   "This is an electronic voucher available for purchase directly through the Telegram bot\n\n"
                   "🎁 Paper Voucher:\n"
                   "In this section, you will learn how to obtain a paper voucher.\n\n"
                   "✅ MY VOUCHERS:\n"
                   "In this section, you will find all the electronic vouchers you have purchased,"
                   " available directly in the Telegram bot.\n\n"
                   "❗IMPORTANT:\n"
                   "Paper vouchers purchased from the tattoo master are not displayed in MY VOUCHERS."
        ,
        'price_info': "😍 Choose the amount for the voucher\n❗Price in Polish Zloty (PLN)",
        'price_more_info': "If the voucher exceeds the amount of 1000 PLN, you need to contact the artist!\n"
                           "Here are his contact details📱:",
        'paper_voucher': "🎁 A paper voucher from the artist is not only an opportunity to receive high-quality service but also a unique souvenir to remember.\n\n"
                         "The paper voucher will make a great gift for your loved ones, bringing unforgettable emotions and a professional touch.\n\n"
                         "To purchase the voucher, contact the artist!\n"
                         "Contacts📱:",
        'payment': "You choose %s PLN.\n\n"
                   "✅If price is correct click [PAY]\n"
                   "🔁For change price click [CHANGE PRICE]\n\n"
                   "Your DarkSoulCode code for payment:\n\n"
                   "🔴 %s 🔴\n\n"
                   "Enter it when making the payment in the 'DarkSoulCode' field❗\n",

        'description_of_voucher': "This voucher is intended for payment for tattoo services by the artist Aleksandr "
                                  "DarkSoul.\n "
                                  "This voucher cannot be:\n\n"
                                  "❌ - Redeemed for cash"
                                  "❌ - Exchanged"
                                  "❌ - Refunded\n\n"
                                  "For more detailed information, please contact the artist!\n",
        'buttons_under_payment': 'Make youre choose',
        'dark_soul_code': 'Your confirmation code for payment 🢂 %s\n'
                          'Enter it when making the payment in the "DarkSoulCode" field.\n',
        'voucher_in_chat': "Congratulations on purchasing a voucher from tattoo master Alexander DarkSoul. 🥳\n\n"

                           "To use the voucher, please provide the code to the tattoo master.\n\n"

                           "IMPORTANT REMINDERS❗\n\n"

                           "❌ - Do not disclose your personal code to third parties.\n"
                           "❌ - Do not publish your code on social media platforms.\n\n"

                           "If someone uses your code, we do not take responsibility for it.\n"
                           "If you want to give the voucher to a third party, "
                           "make sure to pass on the above information\n\n"

                           "Thank you for your purchase, and I wish you a wonderful tattoo-filled day! 🖤\n\n"

                           "DarkSoulAssistant",
        'invalid_payment': "Payment was not made or was unsuccessful😥\n"
                           "If you made a payment and did not receive a voucher,"
                           "please email us at: dark.soul.assistant@gmail.com\n\n"
                           "🚨We will contact you as soon as possible🚨",
        'user_vouchers': "Voucher options:\n\n"
                         "📥 - Download\n"
                         "📭 - Receive via email\n"
                         "👀 - Present to the master\n\n"
                         "IMPORTANT❗\n"
                         "(Once a voucher has been used, it becomes invalid and will not be displayed in this "
                         "section)\n\n"
                         "Thank you for using our service 🖤",
        'successful_payment': f'The payment was successful ✅\n'
                              f'- Amount: %s\n'
                              f'- DarkSoulCode: %s\n'
                              f'- Email: %s',
        'active_vouchers': '✅Choose which voucher you want to receive:',
        'active_vouchers_empty': "❌Unfortunately, there are no purchased vouchers here yet.\n"
                                 "To buy a voucher, go to the menu and select E-Voucher to purchase the electronic "
                                 "version of the voucher.",
        'user_selected_voucher': f"✅You have selected a voucher:\n\n"
                                 f"- ID:  %s \n"
                                 f"- Price: %s PLN\n\n"
                                 f"📥 Select [GET IN CHAT] to receive the voucher in the chat.\n"
                                 f"📭 Select [GET IN EMAIL] to receive the voucher to the email you provided during "
                                 f"payment.\n ",
        'back_btn': '⏪ BACK',
        'main_menu_btn': '⏪ MAIN MENU',
        'my_vouchers_btn': '⏩ MY VOUCHERS'

    },
    'PL': {
        'voucher': "🎁 E-Voucher:\n"
                   "To elektroniczny voucher dostępny do zakupu bezpośrednio przez bota Telegram\n\n"
                   "🎁 Paper Voucher:\n"
                   "W tym dziale dowiesz się, cym jest i jak zdobyć voucher papierowy\n\n"
                   "✅ MY VOUCHERS:\n"
                   "W tym dziale znajdziesz wszystkie elektroniczne vouchery które zakupiłeś-(aś),"
                   " dostępne bezpośrednio w bocie Telegram\n\n"
                   "❗WAŻNE:\n"
                   "(Vouchery papierowe zakupione u mistrza tatuażu nie są wyświetlane w MY VOUCHERS)"
        ,
        'price_info': "😍Wybierz kwotę vouchera\n"
                      "❗Cena w polskich złotych (PLN)",
        'price_more_info': "",
        'paper_voucher': "🎁 Papierowy voucher od mistrza to nie tylko możliwość skorzystania z wysokiej jakości usługi, ale także unikalna pamiątka.\n\n"
                         "Papierowy voucher będzie doskonałym prezentem dla bliskich, dając niezapomniane emocje i profesjonalne podejście.\n\n"
                         "Aby zakupić voucher, skontaktuj się z mistrzem!\n"
                         "Kontakty📱:",

        'payment': f"Wybrałeś-(aś) %s PLN.\n\n"
                   f"✅Aby zapłacić, kliknij [PAY]\n"
                   f"🔁Zmienić cenę, kliknij [CHANGE PRICE]\n\n"
                   f"Twój kod potwierdzający płatność:\n\n🔴 %s 🔴\n\n"
                   "Wpisz go podczas dokonywania płatności w polu 'DarkSoulCode'❗\n",

        'description_of_voucher': "Ten voucher jest przeznaczony na zapłatę usług tatuażu u artysty Aleksandr "
                                  "DarkSoul.\n"
                                  "Ten voucher nie można:\n\n"
                                  "❌ - Wymienić na gotówkę,"
                                  "❌ - Wymienić na inny"
                                  "❌ - Zwrócić\n\n"
                                  "Aby uzyskać bardziej szczegółowe informacje, skontaktuj się z artystą!\n",
        'buttons_under_payment': "[PAY] - Przejdź do płatności\n"
                                 "[CHANGE PRICE] - Zmień kwotę vouchera\n"
                                 "[CHECK PAYMENT] - Potwierdź płatność",
        'voucher_in_chat': "Gratuluję zakupu vouchera u mistrza tatuażu Aleksandra DarkSoul. 🥳\n\n"

                           "Aby skorzystać z vouchera, proszę podać kod mistrzowi tatuażu.\n\n"

                           "WAŻNE PAMIĘTAĆ❗\n\n"

                           "❌ Nie udostępniaj swojego osobistego kodu osobom trzecim.\n"
                           "❌ Nie publikuj swojego kodu w mediach społecznościowych.\n\n"

                           "Jeśli ktoś użyje Twojego kodu, nie ponosimy za to odpowiedzialności.\n"
                           "Jeśli chcesz podarować voucher osobie trzeciej, upewnij się, że przekazujesz powyższe "
                           "informacje\n"

                           "Dziękuję za zakup i życzę Ci wspaniałego dnia pełnego tatuaży! 🖤\n\n"

                           "DarkSoulAssistant",
        'invalid_payment': "Płatność nie została dokonana lub była nieudana😥\n"
                           "Jeśli dokonałeś płatności i nie otrzymałeś vouchera,"
                           "prosimy o kontakt mailowy pod adresem: dark.soul.assistant@gmail.com\n\n"
                           "🚨Skontaktujemy się z Tobą tak szybko, jak to możliwe🚨",
        'user_vouchers': "[ACTIVE VOUCHERS] przechowuje twoje aktywne vouchery.\n\n"
                         "Możesz:\n\n"
                         "📥 - Pobrać\n"
                         "📭 - Otrzymać na mail\n"
                         "👀 - Przekazać mistrzowi\n\n"
                         "WAŻNE❗\n"
                         "(Jeśli voucher został wykorzystany, traci ważność i nie będzie wyświetlany w tej sekcji)\n\n"
                         "Dziękujemy za korzystanie z naszej usługi 🖤",
        'successful_payment': f'Płatność zakończona sukcesem ✅\n'
                              f'- Kwota: %s\n'
                              f'- Kod DarkSoul: %s\n'
                              f'- Email: %s',
        'active_vouchers': '✅Wybierz, jaki voucher chcesz otrzymać:',
        'active_vouchers_empty': "❌Niestety, tutaj jeszcze nie ma zakupionych kuponów.\n"
                                 "Aby kupić kupon, przejdź do menu i wybierz E-Voucher, aby zakupić elektroniczną "
                                 "wersję kuponu.",
        'user_selected_voucher': f"✅Wybrano voucher:\n\n"
                                 f"- ID:  %s \n"
                                 f"- Cena: %s PLN\n\n"
                                 f"📥 Wybierz [GET IN CHAT], aby otrzymać voucher w czacie.\n"
                                 f"📭 Wybierz [GET IN EMAIL], aby otrzymać voucher na podany przez Ciebie adres e-mail "
                                 f"podczas płatności.\n ",
        'back_btn': '⏪ Wstecz',
        'main_menu_btn': '⏪ MENU GŁOWNE',
        'my_vouchers_btn': '⏩ MOJE WOUCZERY'
    },
}
