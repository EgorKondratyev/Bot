import pymysql

from databases.auth_data import host, user, password, db_name, port
from log.log import logger


class ComplainsDB:
    """База данных, которая отвечает за информацию жалоб"""
    def __init__(self):
        try:
            self.__base = pymysql.connect(host=host, user=user, password=password, db=db_name, port=port)
            self.__cur = self.__base.cursor()
            self.__cur.execute("""CREATE TABLE IF NOT EXISTS complains(
                user_id BIGINT,
                amount_complains INT
            )""")
            self.__base.commit()
        except Exception as ex:
            logger.warning(f'Возникла ошибка в базе данных "complains"\n\n'
                           f'{ex}')

    def user_exists(self, user_id: int) -> bool:
        self.__cur.execute('SELECT user_id '
                           'FROM complains '
                           'WHERE user_id = %s',
                           (user_id,))
        return len(self.__cur.fetchmany(1)).__bool__()

    def user_add(self, user_id: int):
        self.__cur.execute('INSERT INTO complains(user_id, amount_complains) '
                           'VALUES(%s, %s)',
                           (user_id, 1))
        self.__base.commit()

    def set_complain(self, user_id: int, amount_complains: int):
        self.__cur.execute('UPDATE complains '
                           'SET amount_complains = %s '
                           'WHERE user_id = %s',
                           (amount_complains, user_id))
        self.__base.commit()

    def get_all_info(self) -> tuple:
        self.__cur.execute('SELECT * '
                           'FROM complains')
        return self.__cur.fetchall()

    def get_amount_complains(self, user_id):
        self.__cur.execute('SELECT amount_complains '
                           'FROM complains '
                           'WHERE user_id = %s',
                           (user_id,))
        complains = self.__cur.fetchmany(1)
        if complains:
            return complains[0][0]
        return

    def increment_complains(self, user_id: int):
        complains = self.get_amount_complains(user_id)
        if complains:
            complains += 1
            self.__cur.execute('UPDATE complains '
                               'SET amount_complains = %s '
                               'WHERE user_id = %s', (complains, user_id))
            self.__base.commit()
        else:
            if not self.user_exists(user_id):
                self.user_add(user_id)

    def __del__(self):
        self.__cur.close()
        self.__base.close()


class ChannelDB:
    """Таблица, отвечающая за подписываемые каналы перед использованием бота"""
    def __init__(self):
        try:
            self.__base = pymysql.connect(host=host, user=user, password=password, db=db_name, port=port)
            self.__cur = self.__base.cursor()
            self.__cur.execute("""CREATE TABLE IF NOT EXISTS channel(
                    channel_id TEXT,
                    channel_name TEXT
                )""")
            self.__base.commit()
        except Exception as ex:
            logger.warning(f'Возникла ошибка в базе данных "channel"\n\n'
                           f'{ex}')

    def exists_channel(self, channel_id: str):
        self.__cur.execute('SELECT channel_id '
                           'FROM channel '
                           'WHERE channel_id = %s',
                           (channel_id, ))
        return len(self.__cur.fetchmany(1)).__bool__()

    def add_channel(self, channel_id: str, channel_name: str):
        self.__cur.execute('INSERT INTO channel(channel_id, channel_name) '
                           'VALUES(%s, %s)',
                           (channel_id, channel_name))
        self.__base.commit()

    def get_channels(self) -> tuple:
        self.__cur.execute('SELECT * '
                           'FROM channel')
        return self.__cur.fetchall()

    def delete_channel(self, channel_id):
        self.__cur.execute('DELETE FROM channel '
                           'WHERE channel_id = %s',
                           (channel_id, ))
        self.__base.commit()

    def __del__(self):
        self.__cur.close()
        self.__base.close()


class TopStateDB:
    """Состояние топа "король чата" или же режим"топа" """
    # Status - Если FALSE, то ТОП, если TRUE, то король чата
    def __init__(self):
        try:
            self.__base = pymysql.connect(host=host, user=user, password=password, db=db_name, port=port)
            self.__cur = self.__base.cursor()
            self.__cur.execute("""CREATE TABLE IF NOT EXISTS state_top(
                state BOOL default FALSE
            )""")
            self.__base.commit()
            self.__cur.execute('SELECT state '
                               'FROM state_top')
            if not len(self.__cur.fetchmany(1)).__bool__():
                self.__cur.execute('INSERT INTO state_top(state) '
                                   'VALUES(%s)',
                                   (False, ))
                self.__base.commit()
        except Exception as ex:
            logger.warning(f'Возникла ошибка в базе данных "state_top"\n\n'
                           f'{ex}')

    def set_state(self, state: bool):
        self.__cur.execute('UPDATE state_top '
                           'SET state = %s',
                           (state, ))
        self.__base.commit()

    def get_state(self) -> bool:
        self.__cur.execute('SELECT state '
                           'FROM state_top')
        return self.__cur.fetchmany(1)[0][0]

    def __del__(self):
        self.__cur.close()
        self.__base.close()


class NewsletterDB:
    """База данных, которая будет отвечать за рассылку"""
    # Сюда будут добавляться ВСЕ пользователи, которые когда-либо нажали на кнопку старт
    def __init__(self):
        try:
            self.__base = pymysql.connect(host=host, user=user, password=password, db=db_name, port=port)
            self.__cur = self.__base.cursor()
            self.__cur.execute("""CREATE TABLE IF NOT EXISTS newsletter(
                    user_id BIGINT
                )""")
            self.__base.commit()
        except Exception as ex:
            logger.warning(f'Возникла ошибка в базе данных "state_top"\n\n'
                           f'{ex}')

    def user_exists(self, user_id: int) -> bool:
        self.__cur.execute('SELECT user_id '
                           'FROM newsletter '
                           'WHERE user_id = %s',
                           (user_id, ))
        return len(self.__cur.fetchmany(1)).__bool__()

    def user_add(self, user_id: int):
        self.__cur.execute('INSERT INTO newsletter(user_id) '
                           'VALUES(%s)',
                           (user_id, ))
        self.__base.commit()

    def get_users_id(self) -> tuple:
        self.__cur.execute('SELECT user_id '
                           'FROM newsletter')
        return self.__cur.fetchall()

    def __del__(self):
        self.__cur.close()
        self.__base.close()


class BanUsersDB:
    """База данных, которая будет за забаненных пользователей"""
    def __init__(self):
        try:
            self.__base = pymysql.connect(host=host, user=user, password=password, db=db_name, port=port)
            self.__cur = self.__base.cursor()
            self.__cur.execute("""CREATE TABLE IF NOT EXISTS ban_db(
                    user_id BIGINT
                )""")
            self.__base.commit()
        except Exception as ex:
            logger.warning(f'Возникла ошибка в базе данных "ban_db"\n\n'
                           f'{ex}')

    def exists_user(self, user_id: int) -> bool:
        self.__cur.execute('SELECT user_id '
                           'FROM ban_db '
                           'WHERE user_id = %s',
                           (user_id, ))
        return len(self.__cur.fetchmany(1)).__bool__()

    def user_add(self, user_id: int):
        self.__cur.execute('INSERT INTO ban_db(user_id) '
                           'VALUES(%s)',
                           (user_id, ))
        self.__base.commit()

    def delete_user(self, user_id: int):
        self.__cur.execute('DELETE FROM ban_db '
                           'WHERE user_id = %s',
                           (user_id, ))
        self.__base.commit()

    def __del__(self):
        self.__cur.close()
        self.__base.close()
        

class GiftDB:
    """База данных, которая будет за забаненных пользователей"""
    def __init__(self):
        try:
            self.__base = pymysql.connect(host=host, user=user, password=password, db=db_name, port=port)
            self.__cur = self.__base.cursor()
            self.__cur.execute("""CREATE TABLE IF NOT EXISTS gift_db(
                    one_day BOOL default TRUE,
                    three_day  BOOL default FALSE,
                    no_gift BOOL default FALSE
                )""")
            self.__base.commit()
            self.__cur.execute('SELECT one_day '
                               'FROM gift_db')
            if not len(self.__cur.fetchmany(1)).__bool__():
                self.__cur.execute('INSERT INTO gift_db(one_day, three_day, no_gift) '
                                   'VALUES(%s, %s, %s)',
                                   (True, False, False))
                self.__base.commit()
        except Exception as ex:
            logger.warning(f'Возникла ошибка в базе данных "gift_db"\n\n'
                           f'{ex}')

    def get_gift_one_day(self):
        self.__cur.execute('SELECT one_day '
                           'FROM gift_db')
        gift = self.__cur.fetchmany(1)[0][0]
        return gift

    def get_gift_three_day(self):
        self.__cur.execute('SELECT three_day '
                           'FROM gift_db')
        gift = self.__cur.fetchmany(1)[0][0]
        return gift

    def get_nogift(self):
        self.__cur.execute('SELECT no_gift '
                           'FROM gift_db')
        gift = self.__cur.fetchmany(1)[0][0]
        return gift

    def set_gift(self, one_day: bool = False, three_day: bool = False, no_gift: bool = False):
        self.__cur.execute('UPDATE gift_db '
                           'SET one_day = %s, three_day = %s, no_gift = %s',
                           (one_day, three_day, no_gift))
        self.__base.commit()

    def __del__(self):
        self.__cur.close()
        self.__base.close()


class PaypalSettingsDB:
    """База данных, которая отвечает за client id and client secret"""
    def __init__(self):
        try:
            self.__base = pymysql.connect(host=host, user=user, password=password, db=db_name, port=port)
            self.__cur = self.__base.cursor()
            self.__cur.execute("""CREATE TABLE IF NOT EXISTS settings_paypal(
                    client_id TEXT,
                    client_secret TEXT,
                    mode BOOL DEFAULT TRUE
                )""")
            self.__base.commit()
        except Exception as ex:
            logger.warning(f'Возникла ошибка в базе данных "settings_paypal"\n\n'
                           f'{ex}')

    def exists_paypal(self, client_id) -> bool:
        self.__cur.execute('SELECT client_id '
                           'FROM settings_paypal')
        return self.__cur.fetchmany(1).__len__().__bool__()

    def add_paypal(self, client_secret, client_id, mode: bool = False):
        self.__cur.execute('INSERT INTO settings_paypal(client_id, client_secret, mode) '
                           'VALUES(%s, %s, %s)',
                           (client_id, client_secret, mode))
        self.__base.commit()

    def get_client(self) -> tuple:
        self.__cur.execute('SELECT * '
                           'FROM settings_paypal')
        return self.__cur.fetchall()

    def update_settings(self, client_secret, client_id, mode: bool = False):
        self.__cur.execute('UPDATE settings_paypal '
                           'SET client_secret = %s, client_id = %s, mode = %s',
                           (client_secret, client_id, mode))
        self.__base.commit()

    def __del__(self):
        self.__cur.close()
        self.__base.close()
