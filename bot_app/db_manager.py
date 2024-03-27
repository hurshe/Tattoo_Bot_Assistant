import sqlite3
import datetime

from bot_app.conversation_handler import user_answers

user_answers = user_answers


class DBManager:
    def __init__(self, db_file):
        self.db_file = db_file

    def create_connection(self):
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            return conn
        except sqlite3.Error as e:
            print(e)
        return conn

    def create_users_table(self):
        try:
            conn = self.create_connection()
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                id INTEGER PRIMARY KEY,
                                chat_id INTEGER,
                                message_id INTEGER,
                                user_name VARCHAR,
                                email VARCHAR,
                                selected_lang VARCHAR,
                                previous_lang VARCHAR,
                                selected_func VARCHAR,
                                prev_func VARCHAR,
                                faq_option VARCHAR,
                                selected_price VARCHAR,
                                previous_price VARCHAR,
                                selected_voucher VARCHAR,
                                user_selected_voucher VARCHAR,
                                dark_soul_code VARCHAR
                            )''')
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(e)

    def create_vouchers_table(self):
        try:
            conn = self.create_connection()
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS vouchers (
                                id INTEGER PRIMARY KEY,
                                chat_id INTEGER,
                                voucher_id VARCHAR,
                                date DATETIME,
                                value_of_voucher VARCHAR,
                                is_active BOOLEAN
                            )''')
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(e)

    def get_all_active_voucher_code(self):
        conn = self.create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT voucher_id FROM vouchers WHERE is_active = ?", (True, ))
        selected_vouchers = cursor.fetchall()

        conn.close()
        return selected_vouchers if selected_vouchers is not None else None

    def get_selected_lang(self, chat_id):
        conn = self.create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT selected_lang FROM users WHERE chat_id = ?", (chat_id,))
        selected_lang = cursor.fetchone()
        conn.close()
        return selected_lang[0] if selected_lang is not None else None

    def get_prev_lang(self, chat_id):
        conn = self.create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT previous_lang FROM users WHERE chat_id = ?", (chat_id,))
        previous_lang = cursor.fetchone()
        conn.close()
        return previous_lang[0] if previous_lang is not None else None

    def get_message_id(self, chat_id):
        conn = self.create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT message_id FROM users WHERE chat_id = ?", (chat_id,))
        previous_lang = cursor.fetchone()
        conn.close()
        return previous_lang[0] if previous_lang is not None else None

    def get_selected_func(self, chat_id):
        conn = self.create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT selected_func FROM users WHERE chat_id = ?", (chat_id,))
        selected_func = cursor.fetchone()
        conn.close()
        return selected_func[0] if selected_func is not None else None

    def get_faq_option(self, chat_id):
        conn = self.create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT faq_option FROM users WHERE chat_id = ?", (chat_id,))
        faq_option = cursor.fetchone()
        conn.close()
        return faq_option[0] if faq_option is not None else None

    def get_selected_value(self, chat_id):
        conn = self.create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT selected_price FROM users WHERE chat_id = ?", (chat_id,))
        selected_price = cursor.fetchone()
        conn.close()
        return selected_price[0] if selected_price is not None else None

    def get_statistics_of_vouchers(self, chat_id):
        conn = self.create_connection()
        cursor = conn.cursor()
        people = cursor.execute("SELECT id FROM users").fetchall()
        vouchers = cursor.execute("SELECT * FROM vouchers").fetchall()
        total_amount = cursor.execute("SELECT value_of_voucher FROM vouchers").fetchall()
        last_sold_voucher = cursor.execute("SELECT date FROM vouchers ORDER BY date DESC LIMIT 1").fetchone()
        conn.close()
        amount_people = len(people)
        amount_vouchers = len(vouchers)
        amount_sold_vouchers = sum(int(item[0]) for item in total_amount)
        last_voucher = last_sold_voucher[0] if last_sold_voucher is not None else 'Не было продаж'

        statistics = [amount_people, amount_vouchers, amount_sold_vouchers, last_voucher]
        return statistics if statistics is not None else None

    def add_voucher_to_db(self, chat_id):
        conn = self.create_connection()
        cursor = conn.cursor()
        voucher_code = user_answers.get('question_1')
        voucher_value = user_answers.get('question_2')
        date = datetime.date.today()
        voucher_exists = cursor.execute("SELECT voucher_id = ? FROM vouchers WHERE chat_id = ?",
                                        (voucher_code, chat_id)).fetchone()
        if voucher_exists == voucher_code:
            return False
        else:
            cursor.execute('''INSERT INTO vouchers (chat_id, voucher_id, date, value_of_voucher, is_active)
                              SELECT ?, ?, ?, ?, ? WHERE NOT EXISTS (SELECT 1 FROM vouchers WHERE voucher_id = ?)''',
                           (chat_id, voucher_code, date, voucher_value, True, voucher_code))
        conn.commit()
        conn.close()

    def add_voucher_by_payment(self, chat_id, voucher_code, voucher_value):
        conn = self.create_connection()
        cursor = conn.cursor()
        date = datetime.date.today()
        voucher_exists = cursor.execute("SELECT voucher_id = ? FROM vouchers WHERE chat_id = ?",
                                        (voucher_code, chat_id)).fetchone()
        if voucher_exists == voucher_code:
            return False
        else:
            cursor.execute('''INSERT INTO vouchers (chat_id, voucher_id, date, value_of_voucher, is_active)
                            SELECT ?, ?, ?, ?, ? WHERE NOT EXISTS (SELECT 1 FROM vouchers WHERE voucher_id = ?)''',
                           (chat_id, voucher_code, date, voucher_value, True, voucher_code))
        conn.commit()
        conn.close()

    def get_deactivate_voucher(self, chat_id):
        conn = self.create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT voucher_id, value_of_voucher, date FROM vouchers WHERE is_active = ?", (0,))
        selected_voucher = cursor.fetchall()
        conn.close()
        return selected_voucher if selected_voucher is not None else None

    def get_selected_voucher(self, chat_id):
        conn = self.create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT selected_voucher FROM users WHERE chat_id = ?", (chat_id,))
        selected_voucher = cursor.fetchone()
        conn.close()
        return selected_voucher[0] if selected_voucher is not None else None

    def get_user_selected_voucher(self, chat_id):
        conn = self.create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_selected_voucher FROM users WHERE chat_id = ?", (chat_id,))
        user_selected_voucher = cursor.fetchone()
        conn.close()
        return user_selected_voucher[0] if user_selected_voucher is not None else None

    def get_vouchers_by_user(self, chat_id):
        conn = self.create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT voucher_id, date, value_of_voucher FROM vouchers WHERE chat_id = ? AND is_active = ?", (chat_id, 1))
        selected_voucher = cursor.fetchall()
        conn.close()
        return selected_voucher

    def get_price_voucher(self, chat_id, selected_voucher):
        conn = self.create_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT value_of_voucher FROM vouchers WHERE chat_id = ? AND voucher_id = ?",
                       (chat_id, selected_voucher))
        voucher_price = cursor.fetchone()
        conn.commit()
        conn.close()
        return voucher_price[0] if voucher_price is not None else None

    def activate_voucher(self, chat_id):
        conn = self.create_connection()
        cursor = conn.cursor()

        voucher_id = cursor.execute("SELECT selected_voucher FROM users WHERE chat_id = ?", (chat_id,)).fetchone()
        cursor.execute("UPDATE vouchers SET is_active = ? WHERE voucher_id = ?", (False, str(voucher_id[0])))
        cursor.execute("UPDATE users SET selected_voucher = ? WHERE chat_id = ?", (None, chat_id))

        conn.commit()
        conn.close()

    def clear_unnecessary_data_from_db(self, chat_id):
        conn = self.create_connection()
        cursor = conn.cursor()

        cursor.execute('''UPDATE users SET 
                          faq_option = ?, 
                          selected_func = ?
                          WHERE chat_id = ?''', (None, None, chat_id))

        conn.commit()
        conn.close()

    def delete_prev_func_from_db(self, chat_id):
        conn = self.create_connection()
        cursor = conn.cursor()

        cursor.execute('''UPDATE users SET 
                          prev_func = ?
                          WHERE chat_id = ?''', (None, chat_id))

        conn.commit()
        conn.close()

    def add_dark_soul_code(self, dark_soul_code, chat_id):
        conn = self.create_connection()
        cursor = conn.cursor()

        cursor.execute('''UPDATE users SET dark_soul_code = ? WHERE chat_id = ?''', (dark_soul_code, chat_id))
        conn.commit()
        conn.close()

        return dark_soul_code

    def get_dark_soul_code(self, chat_id):
        conn = self.create_connection()
        cursor = conn.cursor()

        cursor.execute('''SELECT dark_soul_code FROM users WHERE chat_id = ?''', (chat_id,))
        selected_dark_soul_code = cursor.fetchone()

        conn.close()
        return selected_dark_soul_code[0] if selected_dark_soul_code is not None else None

    def add_user_email_in_db(self, chat_id, email):
        conn = self.create_connection()
        cursor = conn.cursor()

        cursor.execute('''UPDATE users SET email = ? WHERE chat_id = ?''', (email, chat_id))
        conn.commit()
        conn.close()

    def get_user_email(self, chat_id):
        conn = self.create_connection()
        cursor = conn.cursor()

        cursor.execute('''SELECT email FROM users WHERE chat_id = ?''', (chat_id,))
        selected_email = cursor.fetchone()

        conn.close()
        return selected_email[0] if selected_email is not None else None

