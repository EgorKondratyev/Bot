from time import time

from databases.payments import VIP


async def check_expiration_vip():
    vip_db = VIP()
    users_id = vip_db.get_all_users_id()   # ((user_id), (user_id) ... )
    if users_id:
        for attribute_user in users_id:
            user_id = attribute_user[0]
            time_user = vip_db.get_unix_time(user_id=user_id)
            current_time = time()
            if current_time > time_user:
                vip_db.delete_vip_user(user_id=user_id)

