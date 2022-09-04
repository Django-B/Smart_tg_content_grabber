from telethon import TelegramClient, events, utils
import config


# Считывание чатов для парсинга
f = open('target_channels.txt', 'r')
chats1 = f.readlines()
f.close()
chats = []
chat_names = []
for chat in chats1:
    chats.append(int(chat.split('|')[0]))
for chat in chats1:
    chat_names.append(chat.split('|')[1].strip())


# keywords = []

# Считывание ключевых слов
# with open('keywords.txt', 'r') as f:
#     lines = f.readlines()
# for key in lines:
#     keywords.append(key.strip())

# print(keywords)



f = open('my_chat.txt', 'r')
forward_chat = int(f.read().strip().split('|')[0])
f.close()
# print(forward_chat)
api_id = config.api_id
api_hash = config.api_hash
session_name = 'session'


client = TelegramClient(session_name, api_id, api_hash)
client.start()

# target_objects = []
# target_ids = []

# for dialog in client.iter_dialogs():
#     # print(dialog.name)
#     if dialog.name in chat_names:
#         # print(dialog.id)
#         target_ids.append(dialog.id)
#         target_objects.append(dialog)
# print(target_ids)
        
# channel_entity = client.get_entity(forward_chat)
print('Start')

@client.on(events.NewMessage(chats=chats)) #можно парсить неограниченное кол-во каналов
async def normal_handler(event):
    try:
        print('123')
        # for i in keywords:
            # if i in event.message.to_dict()['message']:

        msg = event.message
        msg.message += config.code
        # await client.forward_messages(forward_chat, event.message)
        print(event.message)
        await client.send_message(config.bot, msg)

        # chat = await client.get_entity(event.message.to_dict()['peer_id']['channel_id'])
        # link = 'https://t.me/{}/{}'.format(chat.username, event.message.to_dict()['id'])
        # await client.send_message(int(forward_chat), link)

        # print(chat.username)
    except:
        pass


client.run_until_disconnected()
