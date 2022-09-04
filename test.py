from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
import config
from pprint import pprint
import json
import asyncio


api_id = config.api_id
api_hash = config.api_hash
session_name = 'session2'

f = open('history.json', 'r')
info = json.loads(f.read())
f.close()


client = TelegramClient(session_name, api_id, api_hash)
client.start()

async def all_message(channel, count, iter_count, sleep_):

	i = 0
	while i != iter_count:
		i+=1
		history = await client(GetHistoryRequest(
				peer=channel,
				offset_id=0,
				offset_date=None, add_offset=0,
				limit=count, max_id=0, min_id=0,
				hash=0))
		
		if not history.messages:
			print('Это было последнее сообщение')
			return

		for msg in history.messages:
			dict_ = msg.to_dict()
			# pprint(dict_)
			# print(msg.message)

			if dict_['media']:
				print('media')
			else:
				print('no media')
			
			new_msg = msg
			new_msg.message += config.code
			await client.send_message(config.bot, new_msg)

			await asyncio.sleep(sleep_)
		# print(len(history.messages))

async def main():
	# channel = 'https://t.me/fdasfadsg'
	# channel = 'https://t.me/safinquotes'
	print(info)
	channel = info['link']
	count = info['count'] if info['count'] <= 100 else 100
	iter_count = info['iter_count']
	sleep_ = info['sleep']*60
	


	await all_message(channel, count, iter_count, sleep_)

client.loop.run_until_complete(main())

# async def dump_all_messages(channel):
# 	offset_msg = 0    # номер записи, с которой начинается считывание
# 	limit_msg = 100   # максимальное число записей, передаваемых за один раз

# 	all_messages = []   # список всех сообщений
# 	total_messages = 0
# 	total_count_limit = 0  # поменяйте это значение, если вам нужны не все сообщения

# 	# class DateTimeEncoder(json.JSONEncoder):
# 	# 	'''Класс для сериализации записи дат в JSON'''
# 	# 	def default(self, o):
# 	# 		if isinstance(o, datetime):
# 	# 			return o.isoformat()
# 	# 		if isinstance(o, bytes):
# 	# 			return list(o)
# 	# 		return json.JSONEncoder.default(self, o)

# 	i = 0 
# 	print('Начало')

# 	# RUN = True

# 	while True:
# 		history = await client(GetHistoryRequest(
# 								peer=channel,
# 								offset_id=offset_msg,
# 								offset_date=None, add_offset=0,
# 								limit=limit_msg, max_id=0, min_id=0,
# 								hash=0))
# 		if not history.messages:
# 			print('\n!!!!!!!!!!!!!!!!!!!!ПОСЛЕДНЕЕ СООБЩЕНИЕ!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
# 			break
# 		# print(history.messages)
# 		messages = history.messages
# 		for message in messages:

# 			# if i == 3000:
# 			# 	RUN = False
# 			# 	break

# 			info = message.to_dict()
# 			i+=1
# 			# print(info)
# 			if 'message' in info:
# 				if '#' in info['message']:
# 					print(info['message'])

# 					extract_data(info['message'])

# 					print(f'Num: {i}')
# 					print('-----------------------------------------------------------------')

		

# 		offset_msg = messages[len(messages) - 1].id
# 		total_messages = len(all_messages)
# 		if total_count_limit != 0 and total_messages >= total_count_limit:
# 			break
