from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler


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