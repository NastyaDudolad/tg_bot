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

        # Client choose the time. Write it in the booked_times table
        self.cursor.execute(f'INSERT INTO booked_times(schedule_id) VALUES ({number})')
        self.connection.commit()

        # Find out the id of the last record
        result = self.cursor.execute(f'SELECT id FROM booked_times WHERE schedule_id={number} ORDER BY id DESC LIMIT 1')
        parsed_row = result.fetchall()
        id = parsed_row[0][0]

        # Insert data to the table orders
        # booked_times_id relevant to id in the booked_times and info about client and phone
        self.cursor.execute('''INSERT INTO orders(booked_times_id, client, phone) VALUES (?, ?, ?)''',
                            (id, name, phone))
        self.connection.commit()
        # self.connection.close()

    def delete_booked_time(self):
        self.cursor.execute('DELETE FROM orders WHERE id = ?', (id))
        self.connection.commit()


if __name__ == '__main__':
    print('Not here please')
