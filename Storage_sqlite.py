import sqlite3
import config


class Storage:
    def __init__(self):
        self.connection = sqlite3.connect(config.DATABASE)
        self.cursor = self.connection.cursor()

    def get_free_windows(self):
        result = self.cursor.execute('''
        SELECT
            s.id,
            d.date_info,
            wt.time_info
        FROM schedule s
        JOIN dates d
        ON s.date_id=d.id
        JOIN working_times wt
        ON s.time_id=wt.id
        WHERE s.id NOT IN
        (SELECT bt.schedule_id FROM booked_times bt)
        ''')

        return result.fetchall()

    def get_work_schedule(self):
        result = self.cursor.execute('''
        SELECT time_info FROM working_times
        ''')

        return result.fetchall()

    def add_booked_time(self, order_dict):
        name = order_dict['name']
        phone = order_dict['phone']
        number = int(order_dict['number'])
        chat_id = int(order_dict['chat_id'])

        # Client choose the time. Write it in the booked_times table
        self.cursor.execute(f'INSERT INTO booked_times(schedule_id) VALUES ({number})')
        self.connection.commit()

        # Find out the id of the last record
        result = self.cursor.execute(f'SELECT id FROM booked_times WHERE schedule_id={number} ORDER BY id DESC LIMIT 1')
        parsed_row = result.fetchall()
        id = parsed_row[0][0]

        # Insert data to the table orders
        # booked_times_id relevant to id in the booked_times and info about client and phone
        self.cursor.execute('''INSERT INTO orders(booked_times_id, client, phone, chat_id) VALUES (?, ?, ?, ?)''',
                            (id, name, phone, chat_id))
        self.connection.commit()
        # self.connection.close()

    def delete_booked_time(self, time_id):
        # Find id in booked_times relevant to given schedule_id
        result = self.cursor.execute(f'SELECT * FROM booked_times WHERE schedule_id = {time_id}')
        parsed_row = result.fetchall()
        booked_times_id = parsed_row[0][0]

        # Delete from booked_times and orders simulteniously
        self.cursor.execute(f'DELETE FROM booked_times WHERE id = {booked_times_id}')
        self.cursor.execute(f'DELETE FROM orders WHERE booked_times_id = {booked_times_id}')
        self.connection.commit()

    def get_booking_by_id(self, order_id):
        sql = f'''
        SELECT o.chat_id 
        FROM booked_times AS bt
        LEFT JOIN orders AS o
        ON bt.id = o.booked_times_id
        WHERE bt.schedule_id = {order_id} 
        LIMIT 1
        '''
        result = self.cursor.execute(sql)
        parsed_record = result.fetchone()
        chat_id = 0

        if result.fetchone():
            chat_id = parsed_record[0]

        return chat_id


if __name__ == '__main__':
    print('Not here please')
