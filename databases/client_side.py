import pymysql

from databases.auth_data import host, user, password, db_name
from log.log import logger


class RegisterUserDB:
    """База данных, которая содержит в себе элементы регистрации, профиля, а также служит для проверки зарегистрирован ли
    пользователь"""
    # user_id - Пользователь, к которому относятся данные параметры.
    # user_active - Параметр, отвечающий за активность пользователя в течение 24 часов (BOOL).
    # evaluated_users - Параметр, содержащий ID пользователей, которых user_id оценил в TEXT. user_id_1, user_id_2 ...
    # time_user_active - Параметр, содержащий последнюю активность пользователя в боте в UNIX time (Учитываются только
    # лайки и просмотр анкет)
    # Все остальные параметры age, ..., instagram - это элементы профиля
    @logger.catch()
    def __init__(self):
        try:
            self.__base = pymysql.connect(host=host, user=user, password=password, db=db_name)
            self.__cur = self.__base.cursor()
            self.__cur.execute("""CREATE TABLE IF NOT EXISTS register_user(
                user_id BIGINT,
                status_register BOOL default False,
                status_bot BOOL default False,
                age INT,
                user_sex TEXT,
                interesting_sex TEXT,
                city TEXT,
                name_user TEXT,
                description_user TEXT,
                photo TEXT,
                video TEXT,
                instagram TEXT,
                user_active BOOL default True,
                evaluated_users TEXT,
                time_user_active BIGINT
            )""")
            self.__base.commit()
        except Exception as ex:
            logger.warning(f'Возникла ошибка в базе данных "register_user"\n\n'
                           f'{ex}')

    def get_all_user_id(self) -> tuple:
        self.__cur.execute('SELECT user_id '
                           'FROM register_user')
        return self.__cur.fetchall()

    def user_exists(self, user_id: int) -> bool:
        self.__cur.execute('SELECT user_id '
                           'FROM register_user '
                           'WHERE user_id = %s',
                           (user_id, ))
        return len(self.__cur.fetchmany(1)).__bool__()

    def user_add(self, user_id: int, age: int, user_sex: str, interesting_sex: str, city: str, name_user: str,
                 description_user: str, photo: str = None, video: str = None, bot: bool = False):
        status_register = True
        self.__cur.execute('INSERT INTO '
                           'register_user(user_id, age, user_sex, interesting_sex, city, name_user, description_user,'
                           ' photo, video, status_register, status_bot) '
                           'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                           (user_id, age, user_sex, interesting_sex, city, name_user, description_user, photo, video,
                            status_register, bot))
        self.__base.commit()

    def user_update(self, user_id: int, age: int, user_sex: str, interesting_sex: str, city: str, name_user: str,
                    description_user: str, photo: str = None, video: str = None):
        self.__cur.execute('UPDATE register_user '
                           'SET age = %s, user_sex = %s, interesting_sex =  %s, city = %s, '
                           'name_user = %s, description_user = %s, photo =  %s, video = %s '
                           'WHERE user_id = %s',
                           (age, user_sex, interesting_sex, city, name_user, description_user, photo, video, user_id))
        self.__base.commit()

    def photo_update(self, photo_id: str, user_id: int):
        self.__cur.execute('UPDATE register_user '
                           'SET photo = %s '
                           'WHERE user_id = %s',
                           (photo_id, user_id))
        self.__base.commit()

    def description_update(self, description: str, user_id: int):
        self.__cur.execute('UPDATE register_user '
                           'SET description_user = %s '
                           'WHERE user_id = %s',
                           (description, user_id))
        self.__base.commit()

    def name_update(self, name: str, user_id: int):
        self.__cur.execute('UPDATE register_user '
                           'SET name_user = %s '
                           'WHERE user_id = %s',
                           (name, user_id))
        self.__base.commit()

    def age_update(self, age: int, user_id: int):
        self.__cur.execute('UPDATE register_user '
                           'SET age = %s '
                           'WHERE user_id = %s',
                           (age, user_id))
        self.__base.commit()

    def sex_update(self, sex: str, user_id: int):
        self.__cur.execute('UPDATE register_user '
                           'SET user_sex = %s '
                           'WHERE user_id = %s',
                           (sex, user_id))
        self.__base.commit()

    def interesting_sex_update(self, interesting_sex: str, user_id: int):
        self.__cur.execute('UPDATE register_user '
                           'SET interesting_sex = %s '
                           'WHERE user_id = %s',
                           (interesting_sex, user_id))
        self.__base.commit()

    def update_instagram(self, login_instagram, user_id: int):
        self.__cur.execute('UPDATE register_user '
                           'SET instagram = %s '
                           'WHERE user_id = %s',
                           (login_instagram, user_id))
        self.__base.commit()

    def delete_instagram(self, user_id: int):
        instagram = None
        self.__cur.execute('UPDATE register_user '
                           'SET instagram = %s '
                           'WHERE user_id = %s',
                           (instagram, user_id))
        self.__base.commit()

    def get_all_info_by_user_id(self, user_id: int) -> tuple:
        """Получение всей информации о User по его user_id"""
        # С шансом в 99% будет возвращаться всегда полный info, так как пользователя всегда перенаправляет на
        # регистрацию
        self.__cur.execute('SELECT * '
                           'FROM register_user '
                           'WHERE user_id = %s', (user_id, ))
        info = self.__cur.fetchall()
        return info

    def get_status_bot_by_user_id(self, user_id: int):
        self.__cur.execute('SELECT status_bot '
                           'FROM register_user '
                           'WHERE user_id = %s', (user_id,))
        status_bot = self.__cur.fetchmany(1)
        if status_bot:
            return status_bot[0][0]
        return status_bot

    @staticmethod
    def definition_sex(user_sex: str):
        """Переопределяет обычный текст user_sex в interesting_sex"""
        # Example: "я парень" -> "парни"
        if 'я парень' in user_sex:
            return 'парни'
        elif 'я девушка' in user_sex:
            return 'девушки'
        else:
            return 'все равно'

    def get_users_id_by_interesting_sex(self, interesting_sex: str, user_sex: str) -> list:
        """Получение ID всех юзеров (включая их интересы) конкретного пола"""
        # Здесь также учитываются интересы всех тех людей, которых мы будем выбирать из базы данных, то есть, если у
        # пользователя (который выбирает ID других пользователей) стоит мужской пол, а у ID, которого мы берём из
        # БД стоит интерес лишь к девушкам, то мы его скипаем
        if 'парни' in interesting_sex:
            sex = 'я парень'
            # Выбираем те ID, у которых соответствующий пол, они активны, а также при помощи interesting_sex
            # удостоверимся, что данный ID также интересуется полом или же ему все равно
            interesting_sex_evaluated = self.definition_sex(user_sex)
            user_active = True
            self.__cur.execute('SELECT user_id '
                               'FROM register_user '
                               'WHERE user_sex = %s and user_active = %s and interesting_sex = %s or '
                               'user_active = %s and interesting_sex = %s'
                               'LIMIT 0, 1000',
                               (sex, user_active, 'все равно', user_active, interesting_sex_evaluated))
            users_id = []
            users = self.__cur.fetchall()  # ((user_id, ), (user_id_2, ), ...)
            for user_id in users:
                users_id.append(user_id[0])
            return users_id

        elif 'девушки' in interesting_sex:
            sex = 'я девушка'
            interesting_sex_evaluated = self.definition_sex(user_sex)
            user_active = True
            self.__cur.execute('SELECT user_id '
                               'FROM register_user '
                               'WHERE user_sex = %s and user_active = %s and interesting_sex = %s or '
                               'user_active = %s and interesting_sex = %s'
                               'LIMIT 0, 1000',
                               (sex, user_active, 'все равно', user_active, interesting_sex_evaluated))
            users_id = []
            users = self.__cur.fetchall()  # ((user_id, ), (user_id_2, ), ...)
            for user_id in users:
                users_id.append(user_id[0])
            return users_id

        else:
            interesting_sex_evaluated = self.definition_sex(user_sex)
            user_active = True
            self.__cur.execute('SELECT user_id '
                               'FROM register_user '
                               'WHERE user_active = %s and interesting_sex = %s or '
                               'user_active = %s and interesting_sex = %s'
                               'LIMIT 0, 1000',
                               (user_active, 'все равно', user_active, interesting_sex_evaluated))
            users_id = []
            users = self.__cur.fetchall()  # ((user_id, ), (user_id_2, ), ...)
            for user_id in users:
                users_id.append(user_id[0])
            return users_id

#######################################################################################################################

    def get_all_user_id_by_true_active(self):
        self.__cur.execute('SELECT user_id '
                           'FROM register_user '
                           'WHERE user_active = %s',
                           (True, ))
        return self.__cur.fetchall()

    def get_user_active(self, user_id: int) -> bool:
        self.__cur.execute('SELECT user_active '
                           'FROM register_user '
                           'WHERE user_id = %s', (user_id, ))
        user_active = self.__cur.fetchmany(1)
        if user_active:
            return user_active[0][0]
        return False

    def update_active(self, active: bool, user_id: int):
        self.__cur.execute('UPDATE register_user '
                           'SET user_active = %s '
                           'WHERE user_id = %s',
                           (active, user_id))
        self.__base.commit()

    def get_unix_time_by_user_id(self, user_id: int) -> int:
        self.__cur.execute('SELECT time_user_active '
                           'FROM register_user '
                           'WHERE user_id = %s',
                           (user_id, ))
        time = self.__cur.fetchmany(1)
        if time:
            return time[0][0]
        return 0

    def update_unix_time(self, user_id: int, unix_time: int):
        self.__cur.execute('UPDATE register_user '
                           'SET time_user_active = %s '
                           'WHERE user_id = %s',
                           (unix_time, user_id))
        self.__base.commit()

    def get_evaluated_users(self, user_id: int) -> list[int:]:
        self.__cur.execute('SELECT evaluated_users '
                           'FROM register_user '
                           'WHERE user_id = %s', (user_id,))
        evaluated_users_text = self.__cur.fetchmany(1)[0][0]
        if evaluated_users_text and evaluated_users_text != 'None':
            evaluated_users = list(map(int, evaluated_users_text.split(',')))
            return evaluated_users
        return []

    def add_evaluated(self, user_id: int, evaluated_id: int):
        """Добавление в БД пользователя, которого user id уже просмотрел/лайкнул"""

        # Проверяем есть ли лайкнутые пользователи в базе данных
        self.__cur.execute('SELECT evaluated_users '
                           'FROM register_user '
                           'WHERE user_id = %s', (user_id,))
        evaluated_users_text = self.__cur.fetchmany(1)[0][0]
        # Если есть, то добавляем через запятую ещё одного
        if evaluated_users_text and evaluated_users_text != 'None':
            evaluated_users_text += f',{evaluated_id}'
        # Если нет, то просто создаем нового
        else:
            evaluated_users_text = str(user_id)

        self.__cur.execute('UPDATE register_user '
                           'SET evaluated_users = %s '
                           'WHERE user_id = %s', (evaluated_users_text, user_id))
        self.__base.commit()

    def delete_evaluated(self, user_id: int, evaluated_id: int):
        evaluated_users = self.get_evaluated_users(user_id)
        evaluated_users.remove(evaluated_id)
        evaluated_users_text = str(evaluated_users).strip('[]')
        self.__cur.execute('UPDATE register_user '
                           'SET evaluated_users = %s '
                           'WHERE user_id = %s', (evaluated_users_text, user_id))
        self.__base.commit()

    def __del__(self):
        self.__cur.close()
        self.__base.close()


class ScoresDB:
    """База данных, которая будет отслеживать "мои оценки" и "кто меня оценил" """
    # user_id - владелец отметок.
    # my_scores - те, кого оценил владелец
    # their_scores - те, кто оценил владельца
    @logger.catch()
    def __init__(self):
        try:
            self.__base = pymysql.connect(host=host, user=user, password=password, db=db_name)
            self.__cur = self.__base.cursor()
            self.__cur.execute("""CREATE TABLE IF NOT EXISTS scores(
                    user_id BIGINT,
                    my_scores BIGINT,
                    their_scores BIGINT,
                    smile TEXT
                )""")
            self.__base.commit()
        except Exception as ex:
            logger.warning(f'Возникла ошибка в базе данных "scores"\n\n'
                           f'{ex}')

    def user_add(self, user_id: int):
        self.__cur.execute('INSERT INTO scores(user_id) '
                           'VALUES(%s)',
                           (user_id, ))
        self.__base.commit()

    def exists_my_score(self, user_id: int, evaluated_id: int) -> bool:
        self.__cur.execute('SELECT my_scores '
                           'FROM scores '
                           'WHERE user_id = %s and my_scores = %s', (user_id, evaluated_id))
        return len(self.__cur.fetchmany(1)).__bool__()

    def exists_their_score(self, user_id: int, evaluated_id: int) -> bool:
        self.__cur.execute('SELECT their_scores '
                           'FROM scores '
                           'WHERE user_id = %s and their_scores = %s', (user_id, evaluated_id))
        return len(self.__cur.fetchmany(1)).__bool__()

    def get_my_score(self, user_id: int) -> tuple:
        """Получение всех ID (my_score) в формате ((ID_1), (ID_2) ... (ID_N))"""
        self.__cur.execute('SELECT my_scores '
                           'FROM scores '
                           'WHERE user_id = %s', (user_id, ))
        return self.__cur.fetchall()

    def get_their_scores(self, user_id: int) -> tuple:
        """Получение всех ID (their_scores) в формате ((ID_1), (ID_2) ... (ID_N))"""
        self.__cur.execute('SELECT their_scores '
                           'FROM scores '
                           'WHERE user_id = %s', (user_id, ))
        return self.__cur.fetchall()

    def get_smile(self, user_id: int, evaluated_id: int) -> str:
        self.__cur.execute('SELECT smile '
                           'FROM scores '
                           'WHERE user_id = %s AND their_scores = %s OR user_id = %s  AND my_scores = %s',
                           (user_id, evaluated_id, user_id, evaluated_id))
        smile = self.__cur.fetchmany(1)
        if smile:
            return smile[0][0]
        return ''

    def get_all_their_smile(self, user_id: int) -> tuple:
        self.__cur.execute('SELECT smile '
                           'FROM scores '
                           'WHERE user_id = %s AND NOT their_scores = %s', (user_id, 0))
        return self.__cur.fetchall()

    def add_my_score(self, user_id: int, smile: str, evaluated_id: int):
        scores = self.get_their_scores(user_id)
        # Так как бот будет выдавать лишь последние 20 аккаунтов, то чистим базу данных на -1
        if len(scores) > 20:
            self.__cur.execute('DELETE FROM scores '
                               'WHERE user_id = %s AND my_scores = %s', (user_id, scores[0]))

        self.__cur.execute('INSERT INTO scores(user_id, my_scores, smile) '
                           'VALUES(%s, %s, %s)',
                           (user_id, evaluated_id, smile))
        self.__base.commit()

    def add_their_score(self, user_id: int, smile: str, evaluated_id: int):
        scores = self.get_their_scores(user_id)
        # Так как бот будет выдавать лишь последние 20 аккаунтов, то чистим базу данных на -1
        if len(scores) > 20:
            self.__cur.execute('DELETE FROM scores '
                               'WHERE user_id = %s and their_scores = %s', (user_id, scores[0]))

        self.__cur.execute('INSERT INTO scores(user_id, their_scores, smile) '
                           'VALUES(%s, %s, %s)',
                           (user_id, evaluated_id, smile))
        self.__base.commit()


class StatisticDB:
    """База данных, которая содержит статистику определенного пользователя"""
    # my_scores - поле содержащее кол-во оценок пользователя за все время.
    # their_score - поле отвечающее за то, сколько человек оценило пользователя.
    # residence_time - поле содержащее время нахождения человека в боте (с момента регистрации) в unix time.
    # amount_my_complain - кол-во жалоб, которые отправил пользователь.
    # amount_their_complain - кол-во жалоб, которые отправили на пользователя
    @logger.catch()
    def __init__(self):
        try:
            self.__base = pymysql.connect(host=host, user=user, password=password, db=db_name)
            self.__cur = self.__base.cursor()
            self.__cur.execute("""CREATE TABLE IF NOT EXISTS statistic(
                                user_id BIGINT,
                                my_scores INT default 0,
                                their_scores INT default 0,
                                residence_time BIGINT default 0,
                                amount_my_complain INT default 0,
                                amount_their_complain INT default 0
                            )""")
            self.__base.commit()
        except Exception as ex:
            logger.warning(f'Возникли проблемы с базой данных "statistic_user"\n\n'
                           f'{ex}')

    def get_all_user_id(self):
        self.__cur.execute('SELECT user_id '
                           'FROM statistic')
        return self.__cur.fetchall()

    def get_all_user_id_and_their_scores(self):
        self.__cur.execute('SELECT user_id, their_scores '
                           'FROM statistic')
        return self.__cur.fetchall()

    def user_add(self, user_id: int, residence_time: int):
        """Добавление пользователя при регистрации с проверкой нахождения его в базе данных"""
        self.__cur.execute('SELECT user_id '
                           'FROM statistic '
                           'WHERE user_id = %s', (user_id, ))
        check_register = len(self.__cur.fetchmany(1)).__bool__()
        if not check_register:
            self.__cur.execute('INSERT INTO statistic(user_id, residence_time) '
                               'VALUES(%s, %s)',
                               (user_id, residence_time))
            self.__base.commit()

    def get_all_info(self, user_id) -> tuple:
        """Получение ВСЕЙ информации о конкретном пользователе по user_id в данной базе данных"""
        self.__cur.execute('SELECT * '
                           'FROM statistic '
                           'WHERE user_id = %s',
                           (user_id, ))
        return self.__cur.fetchall()

    def get_my_scores(self, user_id: int) -> int:
        self.__cur.execute('SELECT my_scores '
                           'FROM statistic '
                           'WHERE user_id = %s',
                           (user_id,))
        my_scores = self.__cur.fetchmany(1)
        if my_scores:
            return my_scores[0][0]
        return 0

    def get_their_scores(self, user_id: int) -> int:
        self.__cur.execute('SELECT their_scores '
                           'FROM statistic '
                           'WHERE user_id = %s',
                           (user_id,))
        their_scores = self.__cur.fetchmany(1)
        if their_scores:
            return their_scores[0][0]
        return 0

    def get_residence_time(self, user_id: int) -> int:
        self.__cur.execute('SELECT residence_time '
                           'FROM statistic '
                           'WHERE user_id = %s',
                           (user_id,))
        return self.__cur.fetchmany(1)[0][0]

    def get_amount_my_complain(self, user_id: int) -> int:
        self.__cur.execute('SELECT amount_my_complain '
                           'FROM statistic '
                           'WHERE user_id = %s',
                           (user_id,))
        amount_my_complain = self.__cur.fetchmany(1)
        if amount_my_complain:
            return amount_my_complain[0][0]
        return 0

    def get_amount_their_complain(self, user_id: int) -> int:
        self.__cur.execute('SELECT amount_their_complain '
                           'FROM statistic '
                           'WHERE user_id = %s',
                           (user_id,))
        amount_their_complain = self.__cur.fetchmany(1)
        if amount_their_complain:
            return amount_their_complain[0][0]
        return 0

    def increment_my_scores(self, user_id: int):
        scores = self.get_my_scores(user_id)
        scores += 1
        self.__cur.execute('UPDATE statistic '
                           'SET my_scores = %s '
                           'WHERE user_id = %s',
                           (scores, user_id))
        self.__base.commit()

    def increment_their_scores(self, user_id: int):
        scores = self.get_their_scores(user_id)
        scores += 1
        self.__cur.execute('UPDATE statistic '
                           'SET their_scores = %s '
                           'WHERE user_id = %s',
                           (scores, user_id))
        self.__base.commit()

    def increment_amount_my_complain(self, user_id: int):
        scores = self.get_amount_my_complain(user_id)
        scores += 1
        self.__cur.execute('UPDATE statistic '
                           'SET amount_my_complain = %s '
                           'WHERE user_id = %s',
                           (scores, user_id))
        self.__base.commit()

    def increment_amount_their_complain(self, user_id: int):
        scores = self.get_amount_their_complain(user_id)
        scores += 1
        self.__cur.execute('UPDATE statistic '
                           'SET amount_their_complain = %s '
                           'WHERE user_id = %s',
                           (scores, user_id))
        self.__base.commit()

    def __del__(self):
        self.__cur.close()
        self.__base.close()


class TopDB:
    """База данных, которая содержит статистику топа"""
    @logger.catch()
    def __init__(self):
        try:
            self.__base = pymysql.connect(host=host, user=user, password=password, db=db_name)
            self.__cur = self.__base.cursor()
            self.__cur.execute("""CREATE TABLE IF NOT EXISTS top(
                                    user_id BIGINT,
                                    amount_their_scores INT,
                                    average_their_scores FLOAT,
                                    place INT
                                )""")
            self.__base.commit()
        except Exception as ex:
            logger.warning(f'Возникли проблемы с базой данных "top"\n\n'
                           f'{ex}')

    def exists_user(self, user_id: int) -> bool:
        self.__cur.execute('SELECT user_id '
                           'FROM top '
                           'WHERE user_id = %s', (user_id,))
        return len(self.__cur.fetchmany(1)).__bool__()

    def add_user(self, user_id: int, amount_their_scores: int, average_their_scores: float, place: int):
        self.__cur.execute('INSERT INTO top(user_id, amount_their_scores, average_their_scores, place) '
                           'VALUES(%s, %s, %s, %s)',
                           (user_id, amount_their_scores, average_their_scores, place))
        self.__base.commit()

    def update_user(self, user_id: int, amount_their_scores: int, average_their_scores: float, place: int):
        self.__cur.execute('UPDATE top '
                           'SET amount_their_scores = %s, average_their_scores = %s, place = %s '
                           'WHERE user_id = %s',
                           (amount_their_scores, average_their_scores, place, user_id))
        self.__base.commit()

    def delete_all(self):
        self.__cur.execute('DELETE FROM top')
        self.__base.commit()

    def get_top_users(self) -> tuple:
        self.__cur.execute('SELECT * '
                           'FROM top')
        return self.__cur.fetchall()


class ReferralDB:
    """База данных, отвечающая за реферальную систему"""

    @logger.catch()
    def __init__(self):
        try:
            self.__base = pymysql.connect(host=host, user=user, password=password, db=db_name)
            self.__cur = self.__base.cursor()
            self.__cur.execute("""CREATE TABLE IF NOT EXISTS referral(
                user_id BIGINT,
                referral_id BIGINT
            )""")
            self.__base.commit()
        except Exception as ex:
            logger.warning(f'Возникли проблемы с базой данных "referral"\n\n'
                           f'{ex}')

    def referral_exists(self, referral: int) -> bool:
        self.__cur.execute('SELECT referral_id '
                           'FROM referral '
                           'WHERE referral_id = %s',
                           (referral, ))
        return len(self.__cur.fetchmany(1)).__bool__()

    def referral_add(self, user_id: int, referral: int):
        self.__cur.execute('INSERT INTO referral(user_id, referral_id) '
                           'VALUES(%s, %s)',
                           (user_id, referral))
        self.__base.commit()

    def get_amount_referral(self, user_id: int) -> int:
        self.__cur.execute('SELECT referral_id '
                           'FROM referral '
                           'WHERE user_id = %s',
                           (user_id, ))
        return len(self.__cur.fetchall())


# Формат
# my_scores - те, кого оценил владелец user_1_smile, user_2_smile ... user_n_smile
# their_scores - те, кто оценил владельца user_1_smile, user_2_smile ... user_n_smile
# class ScoresDB:
#     """База данных, которая будет отслеживать "мои оценки" и "кто меня оценил" """
#     # user_id - владелец отметок.
#     # my_scores - те, кого оценил владелец
#     # their_scores - те, кто оценил владельца
#     @logger.catch()
#     def __init__(self):
#         try:
#             self.__base = pymysql.connect(host=host, user=user, password=password, db=db_name)
#             self.__cur = self.__base.cursor()
#             self.__cur.execute("""CREATE TABLE IF NOT EXISTS scores(
#                     user_id BIGINT,
#                     my_scores TEXT,
#                     their_scores TEXT,
#                     smile TEXT
#                 )""")
#             self.__base.commit()
#         except Exception as ex:
#             logger.warning(f'Возникла ошибка в базе данных "scores"\n\n'
#                            f'{ex}')
#
#     def user_add(self, user_id: int):
#         self.__cur.execute('INSERT INTO scores(user_id) '
#                            'VALUES(%s)',
#                            (user_id, ))
#         self.__base.commit()
#
#     def exists_my_score(self, user_id: int, evaluated_id: int) -> bool:
#         try:
#             scores = self.get_my_scores(user_id)
#             print(scores)
#             print(evaluated_id)
#             if scores is not None:
#                 for score in scores:
#                     if score[:3] == f'{evaluated_id}':
#                         return False
#             return True
#         except AttributeError:
#             return True
#
#     def exists_their_score(self, user_id: int, evaluated_id: int) -> bool:
#         try:
#             scores = self.get_heir_scores(user_id)
#             if scores is not None:
#                 for score in scores:
#                     if score[:3] == f'{evaluated_id}':
#                         return False
#             return True
#         except AttributeError:
#             return True
#
#     @staticmethod
#     def get_user_id_and_smile(scores: list[str]):
#         """Разбираем на части ID evaluated и smile (оценку пользователя)"""
#         smile = []
#         evaluated_users = []
#
#         for evaluated_user_text in scores:
#             info = evaluated_user_text.split('_')  # Преобразуем в [userID, smile]
#             evaluated_users.append(info[0])
#             smile.append(info[1])
#         evaluated_users = list(map(int, evaluated_users))
#         return evaluated_users, smile
#
#     def get_my_scores(self, user_id: int) -> list[str:]:
#         # return [id1_smile, id2_smile, ..., idn_smile]
#         try:
#             self.__cur.execute('SELECT my_scores '
#                                'FROM scores '
#                                'WHERE user_id = %s', (user_id,))
#             evaluated_users_text = self.__cur.fetchmany(1)[0][0]
#             if evaluated_users_text and evaluated_users_text != 'None':
#                 evaluated_users = evaluated_users_text.split(',')
#                 return evaluated_users
#             return []
#         except IndexError:
#             self.user_add(user_id)
#
#     def get_heir_scores(self, user_id: int) -> list[str:]:
#         try:
#             self.__cur.execute('SELECT their_scores '
#                                'FROM scores '
#                                'WHERE user_id = %s', (user_id,))
#             evaluated_users_text = self.__cur.fetchmany(1)[0][0]
#             if evaluated_users_text and evaluated_users_text != 'None':
#                 evaluated_users = evaluated_users_text.split(',')
#                 return evaluated_users
#             return []
#         except IndexError:
#             self.user_add(user_id)
#
#     def add_my_scores(self, user_id: int, evaluated_id: int, smile: str):
#         """Добавление "моих отметок" в базу данных"""
#         scores = self.get_my_scores(user_id)
#         # Мы не будем отсылать более 20 аккаунтов за раз, поэтому нет смысла засорять базу данных
#         if len(scores) > 20:
#             scores.pop(0)
#         result = f'{evaluated_id}_{smile}'
#         scores.append(result)
#         scores = str(scores).strip('[]').replace("'", '').replace(' ', '')
#
#         self.__cur.execute('UPDATE scores '
#                            'SET my_scores = %s '
#                            'WHERE user_id = %s', (scores, user_id))
#         self.__base.commit()
#
#     def add_their_scores(self, user_id: int, evaluated_id: int, smile: str):
#         """Добавление "моих отметок" в базу данных"""
#         scores = self.get_heir_scores(user_id)
#         # Мы не будем отсылать более 20 аккаунтов за раз, поэтому нет смысла засорять базу данных
#         if len(scores) > 20:
#             scores.pop(0)
#         result = f'{evaluated_id}_{smile}'
#         scores.append(result)
#         scores = str(scores).strip('[]').replace("'", '').replace(' ', '')
#
#         self.__cur.execute('UPDATE scores '
#                            'SET their_scores = %s '
#                            'WHERE user_id = %s', (scores, user_id))
#         self.__base.commit()
#
#     def __del__(self):
#         self.__cur.close()
#         self.__base.close()
