from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
import json
import re
from states import *

import config


bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
# dp.middleware.setup(LoggingMiddleware())

access_users = [x.strip() for x in open('access_users.txt', 'r').readlines()]
target_channels = [x.strip() for x in open('target_channels.txt', 'r').readlines()]

f = open('my_chat.txt', 'r')
my_chat = int(f.read().split('|')[0])
f.close()


async def send_targets():
    with open('target_channels.txt', 'r') as f:
        l = f.readlines()
        print(l)
        l1 = ''
        for i in range(0, len(l)):
            l1 += str(i) + ') ' + l[i].split('|')[1].strip() + '\n'
        return l1

async def add_target_channel(id, name):
    f = open('target_channels.txt', 'r')
    channels_r = f.read()
    if str(id) in channels_r:
        return False
    f.close()
    
    f = open('target_channels.txt', 'r')
    channels_l = f.readlines()
    f.close()
    
    channels_l.append('{}|{}\n'.format(id, name))

    f = open('target_channels.txt', 'w')
    f.writelines(channels_l)
    f.close()

    return True

async def nice_list(list_, sep, start=''):
    nice_list = ''
    for i in list_:
        try:
            nice_list += start + (i.strip()) + sep
        except AttributeError:
            nice_list += start + str(i) + sep
    return nice_list


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    if not message.chat.username in access_users:
        return
    await message.reply("Привет!", reply=False)


@dp.message_handler(state='*', commands=['add_target'])
async def add_target(message: types.Message):
    if not message.chat.username in access_users:
        return
    await Add_Target.forwarded.set()
    await message.reply('Перешлите мне сообщение из нужного канала или отправьте любое сообщение для завершения действия')
@dp.message_handler(state=Add_Target.forwarded)
async def add_target2(message: types.Message, state: FSMContext):
    if 'forward_from_chat' not in message:
        await state.finish()
        await message.reply('Завершение действия')    
        print(message.text)


    adding = await add_target_channel(message.forward_from_chat.id, message.forward_from_chat.title)
    if adding:
        channels = open('target_channels.txt', 'r')
        l = await nice_list(channels, '\n')
        await message.reply(f'Чат({message.forward_from_chat.title}) успешно добавлен.\nВесь список:\n{l}')
        channels.close()
    else:
        await message.reply('Такой канал уже есть в списке')


@dp.message_handler(commands=['targets'])
async def targets(message: types.Message):
    await message.reply('Вывод списка целевых каналов...', reply=False)
    await message.reply(await send_targets(), reply=False)

@dp.message_handler(state='*', commands=['del_target'])
async def targets(message: types.Message):
    if not message.chat.username in access_users:
        return

    await message.reply('Вывод списка целевых каналов...', reply=False)
    await message.reply(await send_targets(), reply=False)
    
    await Del_Target.index.set()
    await message.reply('Для удаления канала из списка, отправьте его номер или отправьте любое сообщение для завершения действия', reply=False)
@dp.message_handler(state=Del_Target.index)
async def add_target2(message: types.Message, state: FSMContext):
    with open('target_channels.txt', 'r') as f:
        l = f.readlines()
    if not message.text.isdigit() or int(message.text) >= len(l):
        await state.finish()
        await message.reply('Завершение действия', reply=False)
        return
    deleted = l[int(message.text)]
    l.pop(int(message.text))
    print(message.text)
    with open('target_channels.txt', 'w') as f:
        f.writelines(l)
    l = await nice_list(l, '\n')
    await message.reply(f'Удален чат: {deleted}\nВесь список:\n{l}', reply=False)


@dp.message_handler(state='*', commands=['change_my_chat'])
async def upd_access_users(message: types.Message):
    if not message.chat.username in access_users:
        return

    await message.reply('Перешлите сообщение из вашего чата или отправьте любое сообщение для завершения действия', reply=False)
    await Change_Chat.forwarded.set()
@dp.message_handler(state=Change_Chat.forwarded)
async def upd_access_users(message: types.Message, state: FSMContext):
    if 'forward_from_chat' not in message:
        await state.finish()
        await message.reply('Завершение действия')
        return
    f = open('my_chat.txt', 'w')
    f.write('{}|{}'.format(message.forward_from_chat.id, message.forward_from_chat.title))
    f.close()

    f = open('my_chat.txt', 'r')
    await message.reply(f'Ваш чат успешно изменен на {f.read().strip()}', reply=False)
    await message.reply('Завершение действия', reply=False)

    await state.finish()
    


@dp.message_handler(state='*', commands=['add_admin'])
async def upd_access_users(message: types.Message):
    await Add_Admin.admin.set()
    await message.reply('Для добавления админа бота отправьте его юзернэйм без символа "@"\nОтправьте точку для отмены', reply=False)
@dp.message_handler(state=Add_Admin)
async def upd_access_users(message: types.Message, state: FSMContext):
    if message.text == '.':
        await state.finish()
        await message.answer('Отмена')
    f = open('access_users.txt', 'r')
    r = f.read()
    f.close()
    new = r+'\n'+message.text
    # print(new)

    f = open('access_users.txt', 'w')
    f.write(new)
    f.close()

    await state.finish()
    await message.answer(f'Новый админ {message.text} добавлен.\nПосмотреть список админов: /admin_list')

@dp.message_handler(state='*', commands=['del_admin'])
async def del_admin(message: types.Message):
    if not message.chat.username in access_users:
        return

    f = open('access_users.txt', 'r')
    lines = f.readlines()
    f.close()
    list_ = []
    for i in range(len(lines)):
        list_.append('{}) {}'.format(i, lines[i]))
    list_ = await nice_list(list_,'\n')

    await Del_Admin.admin.set()
    await message.answer(f'Выберите номер админа для удаления:\n{list_}')
@dp.message_handler(state=Del_Admin.admin)
async def del_admin(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or int(message.text) < 0:
        await state.finish()
        await message.answer('Некорректный ввод :/')
        return

    f = open('access_users.txt', 'r')
    list_ = f.readlines()
    f.close()
    if int(message.text) >= len(list_):
        await state.finish()
        await message.answer('Некорректный ввод :/')
        return

    # print(list_[int(message.text)])
    popped = list_.pop(int(message.text))

    f = open('access_users.txt', 'w')
    f.writelines(list_)
    f.close()

    await state.finish()
    await message.answer(f'Aдмин {popped.strip()} удален.\nПосмотреть список админов: /admin_list')

@dp.message_handler(commands=['admin_list'])
async def handler(message: types.Message):
    f = open('access_users.txt', 'r')
    list_ = f.readlines()
    f.close()

    list_ = await nice_list(list_, '\n')

    await message.answer(f'Список админов бота\n{list_}')


@dp.message_handler(state='*', commands=['add_script'])
async def add_script(message: types.Message):
    if not message.from_user.username in access_users:
        return
    
    await Script.add_script.set()
    await message.answer('Отправьте сценарий для замены в таком формате:\nСЛОВО ИЛИ СЛОВОСОЧЕТАНИЕ ДЛЯ ЗАМЕНЫ & НА ЧТО НУЖНО ЗАМЕНЯТЬ')

@dp.message_handler(state=Script.add_script)
async def add_script(message: types.Message, state: FSMContext):
    if ' & ' not in message.text or len(message.text.split(' & ')) != 2:
        await state.finish()
        await message.answer('Отмена')
        return    
    f = open('replace_scripts.json', 'r')
    scripts = json.loads(f.read())
    f.close()

    scripts.append([message.text.split(' & ')[0], message.text.split(' & ')[1]])

    print(scripts)

    f = open('replace_scripts.json', 'w')
    f.write(json.dumps(scripts))
    f.close()

    await state.finish()
    await message.answer('Добавлен новый сценариев.\nСписок сценариев: /scripts_list')

@dp.message_handler(state='*', commands=['del_script'])
async def add_script(message: types.Message):
    if not message.chat.username in access_users:
        return

    f = open('replace_scripts.json', 'r')
    scripts = json.loads(f.read())
    f.close()
    print(scripts)
    list_ = []
    for i in range(len(scripts)):
        list_.append('{}) {}'.format(i, scripts[i]))
    list_ = await nice_list(list_,'\n')

    await Script.del_script.set()
    await message.answer(f'Выберите номер cкрипта для удаления:\n{list_}')
@dp.message_handler(state=Script.del_script)
async def del_script(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or int(message.text) < 0:
        await state.finish()
        await message.answer('Некорректный ввод :/')
        return

    f = open('replace_scripts.json', 'r')
    list_ = json.loads(f.read())
    f.close()
    if int(message.text) >= len(list_):
        await state.finish()
        await message.answer('Некорректный ввод :/')
        return

    # print(list_[int(message.text)])
    popped = list_.pop(int(message.text))

    f = open('replace_scripts.json', 'w')
    f.write(json.dumps(list_))
    f.close()

    await state.finish()
    await message.answer(f'Скрипт {popped} удален.\nПосмотреть список скриптов: /scripts_list')

@dp.message_handler(commands=['scripts_list'])
async def add_script(message: types.Message):
    f = open('replace_scripts.json', 'r')
    scripts = json.loads(f.read())
    f.close()

    view_list = await nice_list(scripts, '\n')

    await message.answer(f'Список сценариев:\n{view_list}')
    

@dp.message_handler(state='*', commands=['change_my_link'])
async def change_link(message: types.Message):
    if not message.chat.username in access_users:
        return

    await My_link.link.set()
    await message.reply('Отправьте вашу ссылку для замены или точку для отмены', reply=False)
@dp.message_handler(state=My_link.link)
async def change_link(message: types.Message, state: FSMContext):
    if message.text=='.':
        await state.finish()
        await message.reply('Отмена')
        return
    f = open('my_link.txt', 'w')
    f.write('{}'.format(message.text))
    f.close()

    f = open('my_link.txt', 'r')
    await state.finish()
    await message.reply(f'Ваша ссылка успешно изменена на {f.read().strip()}', reply=False)
    await message.reply('Завершение действия', reply=False)
    f.close()



async def text_filter(text):
    pass

@dp.message_handler(content_types=['text'])
async def process_help_command(message: types.Message):
    print(message)

    if config.code not in message.text:
        return

    text = await text_filter(message.text)
    
    # await bot.copy_message(chat_id=my_chat, from_chat_id='django_999', message_id=message.message_id)
    # await bot.forward_message(chat_id=my_chat, from_chat_id=my_chat, message_id=message.message_id)
    await bot.send_message(my_chat, text)
    
@dp.message_handler(content_types=['photo'])
async def process_help_command(message: types.Message):
    print(message)

    if config.code not in message.caption:
        return

    text = await text_filter(message.caption)

    await bot.send_photo(my_chat, message.photo[0].file_id ,caption=text)


if __name__ == '__main__':
    print('Start')
    executor.start_polling(dp)

