from aiogram.types import Message
from aiogram.dispatcher import FSMContext

from create_bot.admin_bot import admin_dp
from create_bot.config import admins
from databases.admin_side import PaypalSettingsDB
from states.admin_states.settings_paypal_states import SettingsPaypalFSM


# @admin_dp.message_handler(commands='paypal_settings')
async def get_mode(message: Message):
    if message.from_user.id in admins:
        await message.answer('Вы зашли в меню по изменению настроек Paypal\n\n'
                             'Отправьте мне mode (sandbox или live): ')
        await SettingsPaypalFSM.mode.set()


# @admin_dp.message_handler(state=SettingsPaypalFSM.mode)
async def get_client_id(message: Message, state: FSMContext):
    if message.text == 'stop':
        await state.finish()
        await message.answer('OK')

    if message.text == 'sandbox':
        async with state.proxy() as data:
            data['mode'] = False
            await message.answer('Отправьте мне свой client_id')
            await SettingsPaypalFSM.client_id.set()
    elif message.text == 'live':
        async with state.proxy() as data:
            data['mode'] = True
            await message.answer('Отправьте мне свой client_id')
            await SettingsPaypalFSM.client_id.set()
    else:
        await message.answer('Написать можно только "sandbox", "live" или "stop"')


# @admin_dp.message_handler(state=SettingsPaypalFSM.client_id)
async def get_client_secret(message: Message, state: FSMContext):
    if message.text == 'stop':
        await state.finish()
        await message.answer('OK')

    async with state.proxy() as data:
        data['client_id'] = message.text
        await message.answer('Отправьте теперь мне свой client_secret: ')
        await SettingsPaypalFSM.client_secret.set()


# @admin_dp.message_handler(state=SettingsPaypalFSM.client_secret)
async def change_data(message: Message, state: FSMContext):
    async with state.proxy() as data:
        mode = data['mode']
        client_id = data['client_id']

        secret = message.text
    await state.finish()
    print(secret)
    paypal_db = PaypalSettingsDB()
    if not paypal_db.exists_paypal(client_id=client_id):
        paypal_db.add_paypal(client_id=client_id, client_secret=secret, mode=mode)
    else:
        paypal_db.update_settings(client_id=client_id, client_secret=secret, mode=mode)


def register_handlers_settings_paypal():
    admin_dp.register_message_handler(get_mode, commands='paypal_settings')
    admin_dp.register_message_handler(get_client_id, state=SettingsPaypalFSM.mode)
    admin_dp.register_message_handler(get_client_secret, state=SettingsPaypalFSM.client_id)
    admin_dp.register_message_handler(change_data, state=SettingsPaypalFSM.client_secret)
