# Tattoo Bot Assistant

Welcome to the "Tattoo Master" Telegram bot - your personal assistant for all things related to the tattoo artist!

## Description

This bot provides a wide range of services for tattoo artist clients, including information about the artist's work, services, pricing, as well as tips on preparing for a tattoo and caring for it.

## Key Features

- Get information about the tattoo artist, their work, and portfolio.
- Explore prices for services and special offers.
- "Preparation and Care" section: tips on preparing for a tattoo and caring for it.
- Purchase vouchers for tattoo sessions with the option to send them in chat or via email.
- Contact information for reaching out to the artist.
- Multilingual support: choose your preferred language for communication (RU, ENG, PL)
- Admin panel for the tattoo artist: view sales and bot activity statistics, manage vouchers.

## Installation and Usage

1. Clone the repository.
2. Install the necessary dependencies.
3.  Add .env file with:
     BOT_TOKEN, BOT_USERNAME - you can get in BotFather in telegram (https://web.telegram.org/a/#93372553)
     ADMIN_ID, SUB_ADMIN_ID - write in start_command print(chat_id) that will be your id
    
     STRIPE_API - you can get an stripe api code in (https://stripe.com/en-pl)
     SMTP_USERNAME, SMTP_PASSWORD - you can get in settings GMAIL learn how here (https://www.gmass.co/blog/gmail-smtp/)
5. Create docker image run: docker build -t myapp:latest .
6. Launch the bot run: docker run -d myapp:latest
7. Enjoy the extensive functionality of "Tattoo Master"!

## License

This project is licensed under the [MIT License](LICENSE).

---
[Telegram bot "Tattoo Master"](https://t.me/tattoo_master_bot) | [Official website](https://www.tattoomaster.com)
