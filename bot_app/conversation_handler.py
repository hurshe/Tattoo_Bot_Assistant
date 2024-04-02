from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

"""
Voucher Addition Conversation Functions

These async functions collectively handle a conversation flow for adding a voucher in a Telegram bot application. The 
conversation involves asking the user questions about the voucher details and allowing them to provide answers 
interactively.

Function 1: add_voucher_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str

Initiates the voucher addition process by asking the user the first question about the voucher.
Replies to the user with the first question.
Returns the key corresponding to the first question in the questions dictionary.
Function 2: question_1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str

Stores the user's answer to the first question in the user_answers dictionary.
Asks the user the second question about the voucher.
Replies to the user with the second question.
Returns the key corresponding to the second question in the questions dictionary.
Function 3: question_2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int

Stores the user's answer to the second question in the user_answers dictionary.
Displays the collected voucher details to the user for confirmation, along with options to save or change the details.
Ends the conversation flow.
Returns ConversationHandler.END to signify the end of the conversation.
Function 4: cancel(update: Update, context: ContextTypes.DEFAULT_TYPE)

Cancels the voucher addition process by clearing the user_answers dictionary. Replies to the user indicating that the 
survey has been canceled. These functions are designed to be integrated into a conversation handler within the 
Telegram bot application, allowing for an interactive flow when adding vouchers. Users can provide answers to 
questions sequentially, and the bot guides them through the process with appropriate responses and options. 
Additionally, the cancel function provides a way for users to abort the process if needed."""

questions = {
    'question_1': 'Напишите id для идентификации ваучера',
    'question_2': 'На какую сумму ваучер',
}

user_answers = {}


async def add_voucher_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await update.message.reply_text(questions['question_1'])
    return 'question_1'


async def question_1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    user_answers['question_1'] = update.message.text
    await update.message.reply_text(questions['question_2'])
    return 'question_2'


async def question_2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_answers['question_2'] = update.message.text

    save_button = InlineKeyboardButton('Сохранить', callback_data='save')
    change_button = InlineKeyboardButton('Изменить', callback_data='change')
    back_button = InlineKeyboardButton('⏪ Назад', callback_data='admin')

    keyboard = InlineKeyboardMarkup([[save_button, change_button], [back_button]])

    await delete_messages(update, context)
    await update.message.reply_text(f"ID ваучера: {user_answers.get('question_1')}\n"
                                    f"Сумма ваучера: {user_answers.get('question_2')}", reply_markup=keyboard)

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_answers.clear()
    await update.message.reply_text("Опрос отменён!")


async def delete_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    message_id = update.effective_message.message_id

    await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    for i in range(1, 20):
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id - i)

        except Exception as e:
            return e

    for i in range(1, 20):
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id + i)

        except Exception as e:
            return e