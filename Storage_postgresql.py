import psycopg2
import config


class Storage:
    def __init__(self):
        self.connection = psycopg2.connect(
            dbname=config.DATABASE,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            host=config.DB_HOST,
            port=config.DB_PORT
        )
        self.cursor = self.connection.cursor()

    def get_free_windows(self):
        self.cursor.execute('''
            SELECT
                s.id,
                d.date_info,
                wt.time_info
            FROM schedule s
            JOIN dates d ON s.date_id = d.id
            JOIN working_times wt ON s.time_id = wt.id
            WHERE s.id NOT IN (
                SELECT CAST(bt.schedule_id AS INTEGER) FROM booked_times bt
            )
        ''')
        return self.cursor.fetchall()

    def get_work_schedule(self):
        self.cursor.execute('SELECT time_info FROM working_times')
        return self.cursor.fetchall()

    def add_booked_time(self, order_dict):
        name = order_dict['name']
        phone = order_dict['phone']
        number = int(order_dict['number'])
        chat_id = int(order_dict['chat_id'])

        # Додаємо до booked_times та отримуємо його id
        self.cursor.execute(
            'INSERT INTO booked_times(schedule_id) VALUES (%s) RETURNING id',
            (number,)
        )
        booked_times_id = self.cursor.fetchone()[0]

        # Додаємо до orders
        self.cursor.execute(
            '''
            INSERT INTO orders(booked_times_id, client, phone, chat_id)
            VALUES (%s, %s, %s, %s)
            ''',
            (booked_times_id, name, phone, chat_id)
        )
        self.connection.commit()

    def delete_booked_time(self, time_id):
        # Отримуємо id з booked_times за schedule_id
        self.cursor.execute(
            'SELECT id FROM booked_times WHERE schedule_id = %s',
            (time_id,)
        )
        result = self.cursor.fetchone()
        if result:
            booked_times_id = result[0]

            # Видаляємо з orders
            self.cursor.execute(
                'DELETE FROM orders WHERE booked_times_id = %s',
                (booked_times_id,)
            )

            # Видаляємо з booked_times
            self.cursor.execute(
                'DELETE FROM booked_times WHERE id = %s',
                (booked_times_id,)
            )

            self.connection.commit()

    def get_booking_by_id(self, order_id):
        self.cursor.execute('''
            SELECT o.chat_id
            FROM booked_times AS bt
            LEFT JOIN orders AS o ON bt.id = o.booked_times_id
            WHERE bt.schedule_id = %s
            LIMIT 1
        ''', (order_id,))
        result = self.cursor.fetchone()
        return result[0] if result else 0


if __name__ == '__main__':
    print('Not here please')
