import pymysql

from databases.auth_data import host, user, password, db_name
from log.log import logger


class ComplainsDB:
    """База данных, которая отвечает за информацию жалоб"""
    @logger.catch()
    def __init__(self):
        try:
            self.__base = pymysql.connect(host=host, user=user, password=password, db=db_name)
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
