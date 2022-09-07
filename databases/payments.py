import time
from datetime import datetime

import pymysql

from databases.auth_data import host, user, password, db_name, port
from log.log import logger


class PayPalDB:
    """База данных, которая отвечает за оплаты через систему PayPal"""
    def __init__(self):
        try:
            self.__base = pymysql.connect(host=host, user=user, password=password, db=db_name, port=port)
            self.__cur = self.__base.cursor()
            self.__cur.execute("""CREATE TABLE IF NOT EXISTS payments_paypal(
                user_id BIGINT,
                payments_id TEXT,
                payer_info TEXT
            )""")
            self.__base.commit()
        except Exception as ex:
            logger.warning(f'Возникла ошибка в базе данных "payments (PayPal, Payments.py)"\n\n'
                           f'{ex}')

    def payment_exists(self, payments_id: str) -> bool:
        self.__cur.execute('SELECT payments_id '
                           'FROM payments_paypal '
                           'WHERE payments_id = %s',
                           (payments_id, ))
        return len(self.__cur.fetchmany(1)).__bool__()

    def payment_add(self, user_id: int, payments_id: str):
        self.__cur.execute('INSERT INTO payments_paypal(user_id, payments_id) '
                           'VALUES(%s, %s)',
                           (user_id, payments_id))
        self.__base.commit()

    def __del__(self):
        self.__cur.close()
        self.__base.close()


class VIP:
    """База данных, которая отвечает за VIP"""

    def __init__(self):
        try:
            self.__base = pymysql.connect(host=host, user=user, password=password, db=db_name, port=port)
            self.__cur = self.__base.cursor()
            self.__cur.execute("""CREATE TABLE IF NOT EXISTS vip(
                    user_id BIGINT,
                    VIP BOOL DEFAULT FALSE,
                    time_vip BIGINT DEFAULT 0
                )""")
            self.__base.commit()
        except Exception as ex:
            logger.warning(f'Возникла ошибка в базе данных "vip (PayPal, Payments.py)"\n\n'
                           f'{ex}')

    def exists_user(self, user_id: int):
        self.__cur.execute('SELECT user_id '
                           'FROM vip '
                           'WHERE user_id = %s',
                           (user_id,))
        check_user = len(self.__cur.fetchmany(1)).__bool__()
        return check_user

    def update_status_vip(self, user_id: int, status_vip: bool, time_vip: int):
        check_user = self.exists_user(user_id)
        if not check_user:
            self.__cur.execute('INSERT INTO vip(user_id) '
                               'VALUES(%s)',
                               (user_id, ))
        self.__cur.execute('SELECT time_vip '
                           'FROM vip '
                           'WHERE user_id = %s',
                           (user_id, ))
        time_vip_current = self.__cur.fetchmany(1)[0][0]
        # Если время не равно 0, то мы прибавляем к текущему, чтобы не сбрасывать оставшееся
        if time_vip_current:
            time_vip_current += time_vip
        else:
            time_vip_current = time.time() + time_vip

        self.__cur.execute('UPDATE vip '
                           'SET VIP = %s, time_vip = %s '
                           'WHERE user_id = %s',
                           (status_vip, time_vip_current, user_id))
        self.__base.commit()

    def delete_vip_user(self, user_id: int):
        self.__cur.execute('DELETE FROM vip '
                           'WHERE user_id = %s',
                           (user_id, ))
        self.__base.commit()

    def get_time(self, user_id: int) -> datetime.utcfromtimestamp:
        check_user = self.exists_user(user_id)
        if not check_user:
            self.__cur.execute('INSERT INTO vip(user_id) '
                               'VALUES(%s)',
                               (user_id,))

        self.__cur.execute('SELECT time_vip '
                           'FROM vip '
                           'WHERE user_id = %s',
                           (user_id, ))
        time_vip = self.__cur.fetchmany(1)[0][0]
        our_time = datetime.utcfromtimestamp(time_vip).strftime('%Y-%m-%d %H:%M:%S')
        return our_time

    def get_unix_time(self, user_id: int):
        self.__cur.execute('SELECT time_vip '
                           'FROM vip '
                           'WHERE user_id = %s',
                           (user_id,))
        time_vip = self.__cur.fetchmany(1)
        if time_vip:
            return time_vip[0][0]
        return 0

    def get_all_users_id(self) -> tuple:
        self.__cur.execute('SELECT user_id '
                           'FROM vip')
        return self.__cur.fetchall()

    def __del__(self):
        self.__cur.close()
        self.__base.close()


class KingChatDB:
    """База данных, которая отвечает за содержание королей чата"""
    def __init__(self):
        try:
            self.__base = pymysql.connect(host=host, user=user, password=password, db=db_name, port=port)
            self.__cur = self.__base.cursor()
            self.__cur.execute("""CREATE TABLE IF NOT EXISTS king_chat(
                user_id BIGINT
            )""")
            self.__base.commit()
        except Exception as ex:
            logger.warning(f'Возникла ошибка в базе данных "king chat (Payments.py)"\n\n'
                           f'{ex}')

    def exists_user(self, user_id: int) -> bool:
        self.__cur.execute('SELECT user_id '
                           'FROM king_chat '
                           'WHERE user_id = %s',
                           (user_id, ))
        return len(self.__cur.fetchmany(1)).__bool__()

    def add_user(self, user_id: int):
        self.__cur.execute('INSERT INTO king_chat(user_id) '
                           'VALUES(%s)',
                           (user_id, ))
        self.__base.commit()

    def delete_user(self, user_id: int):
        self.__cur.execute('DELETE FROM king_chat '
                           'WHERE user_id = %s',
                           (user_id, ))
        self.__base.commit()

    def get_users_id(self) -> tuple:
        self.__cur.execute('SELECT user_id '
                           'FROM king_chat')
        return self.__cur.fetchall()

    def __del__(self):
        self.__cur.close()
        self.__base.close()


class PriceDB:
    """База данных, отвечающая за контроль цен"""

    def __init__(self):
        try:
            self.__base = pymysql.connect(host=host, user=user, password=password, db=db_name, port=port)
            self.__cur = self.__base.cursor()
            self.__cur.execute("""CREATE TABLE IF NOT EXISTS price(
                    one_day_price INT default 33,
                    three_day_price INT default 97,
                    week_day_price INT default 200,
                    month_day_price INT default 900,
                    king_chat_price INT default 690
                )""")
            self.__base.commit()
            self.__cur.execute('SELECT * '
                               'FROM price')
            if not len(self.__cur.fetchmany(1)).__bool__():
                self.__cur.execute('INSERT INTO price(one_day_price) '
                                   'VALUES(%s)',
                                   (33, ))
        except Exception as ex:
            logger.warning(f'Возникла ошибка в базе данных "king chat (Payments.py)"\n\n'
                           f'{ex}')

    def update_one_day_price(self, price: int):
        self.__cur.execute('UPDATE price '
                           'SET one_day_price = %s',
                           (price, ))
        self.__base.commit()

    def update_three_day_price(self, price: int):
        self.__cur.execute('UPDATE price '
                           'SET three_day_price = %s',
                           (price,))
        self.__base.commit()

    def update_week_day_price(self, price: int):
        self.__cur.execute('UPDATE price '
                           'SET week_day_price = %s',
                           (price,))
        self.__base.commit()

    def update_month_day_price(self, price: int):
        self.__cur.execute('UPDATE price '
                           'SET month_day_price = %s',
                           (price,))
        self.__base.commit()

    def update_king_chat_price(self, price: int):
        self.__cur.execute('UPDATE price '
                           'SET king_chat_price = %s',
                           (price,))
        self.__base.commit()

    def get_one_day_price(self):
        self.__cur.execute('SELECT one_day_price '
                           'FROM price')
        return self.__cur.fetchmany(1)[0][0]

    def get_three_day_price(self):
        self.__cur.execute('SELECT three_day_price '
                           'FROM price')
        return self.__cur.fetchmany(1)[0][0]

    def get_week_day_price(self):
        self.__cur.execute('SELECT week_day_price '
                           'FROM price')
        return self.__cur.fetchmany(1)[0][0]

    def get_month_day_price(self):
        self.__cur.execute('SELECT month_day_price '
                           'FROM price')
        return self.__cur.fetchmany(1)[0][0]

    def get_king_chat_price(self):
        self.__cur.execute('SELECT king_chat_price '
                           'FROM price')
        return self.__cur.fetchmany(1)[0][0]

    def __del__(self):
        self.__cur.close()
        self.__base.close()
