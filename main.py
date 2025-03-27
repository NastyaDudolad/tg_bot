from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, Update,
                      InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler,
                          ContextTypes, ConversationHandler, MessageHandler, filters)
import config
import Storage
import re


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Hello', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    answer = '''
    Доступные команды:
    /work_schedule
    /sign_up
    /cancel_order
    /free_windows'''
    await update.message.reply_text(answer, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


async def free_windows(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    data = db.get_free_windows()
    schedule_text = "Свободные места:\n"

    for row in data:
        schedule_text += f"Номер записи: {row[0]}, дата: {row[1]}, время: {row[2]}\n"
    await update.message.reply_text(schedule_text, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


async def work_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    data = db.get_work_schedule()
    work_schedule = 'Время работы:\n'
    for row in data:
        work_schedule += f'{row[0]}\n'
    await update.message.reply_text(work_schedule, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

###
# Order cancellation
###
async def cancel_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Введите номер записи:", reply_markup=ReplyKeyboardRemove())
    return 1


async def end_of_cancellation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # delete_number_command(update)
    if re.match(r'^\d+$', update.message.text):
        delete_number = update.message.text
        db.delete_booked_time(delete_number)
        await update.message.reply_text("Вы успешно удалили запись!", reply_markup=ReplyKeyboardRemove())
    else:
        await update.message.reply_text("Не номер", reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


###
# Sign up
###
async def sign_up_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    data = db.get_free_windows()
    sign_up_text = 'Выберите номер записи:\n'

    # Define inline buttons for car color selection
    keyboard = []

    for row in data:
        keyboard.append([InlineKeyboardButton(
            f"Номер записи: /{row[0]}, дата: {row[1]}, время: {row[2]}",
            callback_data=row[0]
        )])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(sign_up_text, reply_markup=reply_markup)
    return 1


async def input_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    input_number = query.data
    current_order['number'] = int(input_number)

    await query.edit_message_text(text='<b>Введите ваше имя:</b>', parse_mode='HTML')
    return 2


async def input_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    name = update.message.text
    current_order['name'] = name
    test = current_order
    await update.message.reply_text(text='<b>Введите ваш телефон:</b>', parse_mode='HTML')
    return 3


async def sign_up_ending(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    phone = update.message.text
    current_order['phone'] = phone
    db.add_booked_time(current_order)
    await update.message.reply_text(text=f"<b>Вы успешно записаны! Ваш номер записи: {current_order['number']}</b>",
                                    parse_mode='HTML')

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Bye! Hope to talk to you again soon.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


db = Storage.Storage()
current_order = {
    'number': 0,
    'name': '',
    'phone': ''
}


def main() -> None:
    """Run the bot."""
    application = Application.builder().token(config.TOKEN).build()

    sign_up_handler = ConversationHandler(
        entry_points=[
            CommandHandler('sign_up', sign_up_start)
        ],
        states={
            1: [CallbackQueryHandler(input_name)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_phone)],
            3: [MessageHandler(filters.TEXT & ~filters.COMMAND, sign_up_ending)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    cancellation_handler = ConversationHandler(
        entry_points=[
            CommandHandler('cancel_order', cancel_order)
        ],
        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, end_of_cancellation)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help))
    application.add_handler(CommandHandler('free_windows', free_windows))
    application.add_handler(CommandHandler('work_schedule', work_schedule))
    application.add_handler(sign_up_handler)
    application.add_handler(cancellation_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
