from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
import json
import re
from states import *
import os
# import subprocess

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

@dp.message_handler(commands=['test'])
async def test(message: types.Message):
    await message.answer('<a href="https://vk.com/id41732290">VK</a>', parse_mode='HTML')



@dp.message_handler(state='*', commands=['add_link_script'])
async def add_link(message: types.Message):
    if not message.from_user.username in access_users:
        return
    
    await Link_Script.add_link.set()
    await message.answer('Отправьте шаблон для замены в таком формате:\nСЛОВО C CCЫЛКОЙ|НА ЧТО НУЖНО ЗАМЕНЯТЬ|ССЫЛКА НА КОТОРУЮ НУЖНО МЕНЯТЬ')

@dp.message_handler(state=Link_Script.add_link)
async def add_link(message: types.Message, state: FSMContext):
    if '|' not in message.text or len(message.text.split('|')) != 3:
        await state.finish()
        await message.answer('Отмена')
        return    
    f = open('entities.json', 'r')
    links = json.loads(f.read())
    f.close()

    links.append(message.text.strip())

    print(links)

    f = open('entities.json', 'w')
    f.write(json.dumps(links))
    f.close()

    await state.finish()
    await message.answer('Добавлен новый шаблонов.\nСписок шаблонов: /link_scripts_list')

@dp.message_handler(state='*', commands=['del_link_script'])
async def add_link(message: types.Message):
    if not message.chat.username in access_users:
        return

    f = open('entities.json', 'r')
    links = json.loads(f.read())
    f.close()
    print(links)
    list_ = []
    for i in range(len(links)):
        list_.append('{}) {}'.format(i, links[i]))
    list_ = await nice_list(list_,'\n')

    await Link_Script.del_link.set()
    await message.answer(f'Выберите номер шаблона для удаления:\n{list_}')
@dp.message_handler(state=Link_Script.del_link)
async def del_link(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or int(message.text) < 0:
        await state.finish()
        await message.answer('Отмена')
        return

    f = open('entities.json', 'r')
    list_ = json.loads(f.read())
    f.close()
    if int(message.text) >= len(list_):
        await state.finish()
        await message.answer('Некорректный ввод :/')
        return

    # print(list_[int(message.text)])
    popped = list_.pop(int(message.text))

    f = open('entities.json', 'w')
    f.write(json.dumps(list_))
    f.close()

    await state.finish()
    await message.answer(f'Шаблон {popped} удален.\nПосмотреть список шаблонов: /link_scripts_list')

@dp.message_handler(commands=['link_scripts_list'])
async def add_link(message: types.Message):
    f = open('entities.json', 'r')
    links = json.loads(f.read())
    f.close()

    view_list = await nice_list(links, '\n')

    await message.answer(f'Список шаблонов:\n{view_list}')



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


@dp.message_handler(state='*', commands=['change_my_username'])
async def change_link(message: types.Message):
    if not message.chat.username in access_users:
        return

    await My_Username.username.set()
    await message.reply('Отправьте ваш юзернэйм без символа @ для замены или точку для отмены', reply=False)
@dp.message_handler(state=My_Username.username)
async def change_link(message: types.Message, state: FSMContext):
    if message.text=='.':
        await state.finish()
        await message.reply('Отмена')
        return
    f = open('my_username.txt', 'w')
    f.write('{}'.format(message.text))
    f.close()

    f = open('my_username.txt', 'r')
    await state.finish()
    await message.reply(f'Ваш юзернэйм успешно изменен на {f.read().strip()}', reply=False)
    await message.reply('Завершение действия', reply=False)
    f.close()


history_status = False
@dp.message_handler(state='*', commands=['copy_history'])
async def history(message: types.Message):
    global history_status
    if not message.chat.username in access_users or history_status:
        await message.answer('Уже выполняется копирование истории')
        return
    history_status = True


    await History.link.set()

    await message.answer('Отправьте ссылку на канал')
@dp.message_handler(state=History.link)
async def history(message: types.Message, state: FSMContext):
    if message.text == '.':
        await state.finish()
        await message.answer('Отмена')

    async with state.proxy() as data:
        data['link'] = message.text
    
    await History.count.set()
    await message.answer('Отправьте количество сообщений, которые нужно скопировать(максимум 100)')
@dp.message_handler(state=History.count)
async def history(message: types.Message, state: FSMContext):
    if message.text == '.' or not message.text.isdigit():
        await state.finish()
        await message.answer('Отмена')
    
    async with state.proxy() as data:
        data['count'] = int(message.text)
    
    await History.iter_count.set()
    await message.answer('Отправьте количество циклов копирования сообщений(-1 = бесконечно)')
@dp.message_handler(state=History.iter_count)
async def history(message: types.Message, state: FSMContext):
    if message.text == '.' or not message.text.isdigit():
        await state.finish()
        await message.answer('Отмена')

    async with state.proxy() as data:
        data['iter_count'] = int(message.text)

    await History.sleep.set()
    await message.answer('Отправьте время задержки между копированием сообщений(в минутах)')
@dp.message_handler(state=History.sleep)
async def history(message: types.Message, state: FSMContext):
    global history_status
    if message.text == '.' or not message.text.isdigit():
        await state.finish()
        await message.answer('Отмена')

    async with state.proxy() as data:
        data['sleep'] = int(message.text)

    info = {
        'link': data['link'],
        'count': data['count'],
        'iter_count': data['iter_count'],
        'sleep': data['sleep']
    }

    f = open('history.json', 'w')
    f.write(json.dumps(info))
    f.close()

    history_status = False
    os.system('python3 test.py &')

    await state.finish()
    await message.answer('Бот начал копирование истории')

    

async def ent_change(text, entities=[], templates=[]):
    # replace text and link
    if not entities:
        return text

    # templates = ['200|3000|https://olim.bek', '500|BONUS|https://olim2.bek']

    # text = 'Всем привет, новый бонус 200 или 500'
    # entities = [
    #     {"type": "text_link", "offset": 25, "length": 3, "url": "http://1.bet/"},
    #     {"type": "text_link",  "offset": 33, "length": 3, "url": "http://1.bet/"}
    # ]
    a = '<a href="{}">'
    b = '</a>'

    new_text = text

    addition = 0        
    status = False
    for ent in entities:
        if ent['type'] != 'text_link':
            continue
        offset = ent['offset']
        length = ent['length']
        txt = text[offset:offset+length]
        if status:
            offset += addition
            length += addition
            txt = new_text[offset:offset+length]
        for temp in templates:
            splt = temp.split('|')

            if splt[0] == txt:
                start = text[:offset]
                end = text[offset+length:]
                if status:
                    start = new_text[:offset]
                    end = new_text[offset+length:]

                
                addition+=len(a.format(splt[2]))
                addition+=len(b)
                addition+=len(splt[1])-len(txt)
                start = start + a.format(splt[2]) + splt[1] + b + end

                new_text = start

                status = True
    
    print('"'+new_text+'"')
    return new_text



async def text_filter(text, entities=[], templates=[]):
    URL_REGEX = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:\'\".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""

    result = text
    result = await ent_change(result, entities, templates)

    # Replace with scripts
    f = open('replace_scripts.json', 'r')
    scripts = json.loads(f.read())
    f.close()
    script_news = []
    # print(scripts)
    for old, new in scripts:
        result = result.replace(old, new)
        result = result.replace(old.lower(), new)
        result = result.replace(old.upper(), new)
        result = result.replace(old.capitalize(), new)
        script_news.append(new)

        
    # Replace static username
    f = open('my_username.txt', 'r')
    username = f.read().strip()
    f.close()

    print(result)
    
    usernames = re.findall(r'@\w+', result)
    for old_name in usernames:

        if old_name in script_news or old_name[1:] in script_news:
            print('yes')
        else:
            print('no')
            # print(result)
            result = result.replace(old_name[1:], username, 1)


    # Replace links
    links = re.findall(URL_REGEX, text)
    # print(f'{links=}')

    f = open('my_link.txt', 'r')
    my_link = f.read().strip()
    f.close()
    # print(my_link)

    for link in links:
        if link[0:12] != 'https://t.me':
            result = result.replace(link, my_link)
    return result

@dp.message_handler(content_types=['text'])
async def process_help_command(message: types.Message):
    print(message)

    # if 'entities' in message:
    #     print(type(message.entities[0]))
    #     print(message.entities)

    if config.code not in message.text:
        return
    
    if 'entities' in message:
        f = open('entities.json', 'r')
        templates1 = json.loads(f.read())
        f.close()
        templates = []
        for template in templates1:
            templates.append(template.strip())

        print(templates)
        text = await text_filter(message.text[:-len(config.code)], message.entities, templates)
    else:
        text = await text_filter(message.text[:-len(config.code)])

    await bot.send_message(my_chat, text, parse_mode='HTML')
    
@dp.message_handler(content_types=['photo'])
async def process_help_command(message: types.Message):
    print(message)


    if config.code not in message.caption:
        return
    
    if 'caption_entities' in message:
        f = open('entities.json', 'r')
        templates1 = json.loads(f.read())
        f.close()
        templates = []
        for template in templates1:
            templates.append(template.strip())

        text = await text_filter(message.caption, message.caption_entities, templates)
    else:
        text = await text_filter(message.caption)

    await bot.send_photo(my_chat, message.photo[0].file_id ,caption=text[:-len(config.code)], parse_mode='HTML')
                                                                                                                                                                                                   

if __name__ == '__main__':
    print('Start')
    # os.system('python3 main.py &')
    # output = subprocess.check_output(['python3', 'main.py', '&'])
    executor.start_polling(dp)

    # print(os.popen('ps').read())
    
        

