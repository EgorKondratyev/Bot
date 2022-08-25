# Если пользователь отсутствует более 24 часов, то деактивируем его аккаунт
import time

from databases.client_side import RegisterUserDB


async def deactivate():
    """Проверка ВСЕХ аккаунтов на активность"""
    register_db = RegisterUserDB()
    users_id = register_db.get_all_user_id_by_true_active()
    for user_id in users_id:
        user_id = user_id[0]
        user_time = register_db.get_unix_time_by_user_id(user_id)
        if register_db.get_unix_time_by_user_id(user_id):
            current_time = time.time()
            remaining_time = current_time - user_time
            if remaining_time >= 1:
                # Деактивируем аккаунт, так как прошло более 1 дня
                register_db.update_active(user_id=user_id, active=False)

