import requests
import time
import sys
import os
import config
import Storage
import re

responded_updates = []

url = f'https://api.telegram.org/bot{config.TOKEN}/'


def send_message(chat_id, text):
    response = requests.get((url + f'sendMessage?chat_id={chat_id}&text={text}'))
    return response.json()


def get_update():
    response = requests.get(url + 'getUpdates?offset=-1')
    return response.json()


def get_message_text(update):
    return update['result'][0]['message']['text']


def get_chat_id(update):
    return update['result'][0]['message']['chat']['id']


def get_update_id(update):
    return update['result'][0]['update_id']


# Functions for processing user commands
def get_id_command(update):
    print('Chat_id', get_chat_id(update))


def help_command(update):
    help_answ = '''
        /work_schedule
        /sign_up
        /cancel_order
        /free_windows
                        '''
    send_message(get_chat_id(update), help_answ)


def free_windows_command(update):
    data = db.get_free_windows()
    schedule_text = "Свободные места:\n"

    for row in data:
        schedule_text += f"Номер записи: {row[0]}, дата: {row[1]}, время: {row[2]}\n"
        # print(f"ID: {row[0]}, Дата: {row[1]}, Время: {row[2]}")

    send_message(get_chat_id(update), schedule_text)


def work_schedule_command(update):
    data = db.get_work_schedule()
    work_schedule = 'Время работы:\n'
    for row in data:
        work_schedule += f'{row[0]}\n'
    send_message(get_chat_id(update), work_schedule)


def sign_up_command(update):
    data = db.get_free_windows()
    sign_up_text = 'Выберите номер записи:\n'
    for row in data:
        sign_up_text += f"Номер записи: /{row[0]}, дата: {row[1]}, время: {row[2]}\n"
    send_message(get_chat_id(update), sign_up_text)


def number_command(update, number):
    order_step = 1
    current_order['number'] = number
    send_message(get_chat_id(update), 'Введите ваше имя и фамилию:')


def end_order():
    db.add_booked_time(current_order)


current_order = {
    'number': 0,
    'name': '',
    'phone': ''
}

command_definitions = {
    '/get_id': get_id_command,
    '/help': help_command,
    '/free_windows': free_windows_command,
    '/work_schedule': work_schedule_command,
    '/sign_up': sign_up_command
}

signup_cancel_functions = ['/get_id', '/help', '/free_windows', '/work_schedule']

db = Storage.Storage()


def main():
    order_step = 0

    while True:
        time.sleep(1)

        try:
            update = get_update()
            text_input = get_message_text(update)

            # Чи немає поточного update_id у списку тих на які відповідали
            # Тоді надаємо відповідь і записуємо update_id до списку тих на які відповідали
            update_id = get_update_id(update)

            if update_id not in responded_updates:
                if order_step == 1:
                    current_order['client'] = text_input
                    send_message(get_chat_id(update), 'Введите ваш номер телефона:')
                    order_step = 2

                if order_step == 2:
                    current_order['phone'] = text_input
                    db.add_booked_time(current_order)
                    send_message(get_chat_id(update), 'Вы успешно записаны!')
                    order_step = 0

                if re.match(r'^/\d+$', text_input):
                    current_order['number'] = text_input[1:]
                    send_message(get_chat_id(update), 'Введите ваше имя:')
                    order_step = 1

                if text_input in command_definitions:
                    command_definitions[text_input](update)

                responded_updates.append(update_id)

        except Exception as e:
            print('Something wrong in main loop:', e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)


if __name__ == '__main__':
    main()
