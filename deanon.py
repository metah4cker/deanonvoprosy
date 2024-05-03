
import pyrogram
import toml
import pyrolog
import sys
import json

from pathlib import Path

####

CONFIG_PATH = Path('./config.toml')  # path to the configuration file
BOT_ADMIN_ID = '5699559152'          # user id of the bot admin

####

# get simple colored logger
logger = pyrolog.get_colored_logger('exception')

# title
logger.info('| {style.bold}{fore.red}DEANON{fore.white}VOPROSY{reset} |')
logger.info('С помощью данного скрипта вы можете')
logger.info('{style.bold}деанонимизровать тех, кто прислал вам анонимное сообщение{reset}')
logger.info('{fore.yellow}{style.bold}{style.dim}https://github.com/ftdot/deanonvoprosy{reset}')

# try to load a configuration
try: 
  config = toml.loads(CONFIG_PATH.read_text())
except Exception as e:
  logger.exception('Ошибка во время парсинга конфигурации.', exc=e)
  sys.exit()

####

# ask for the api id, if it doesn't set
if config['api_id'] == 'ask':
  logger.info('Введите {style.bold}{fore.red}API ID{reset}. Получить можно здесь: https://my.telegram.org')
  config['api_id'] = input(f' {pyrolog.TextColor.green}{pyrolog.TextStyle.bold}*{pyrolog.TextStyle.reset} {pyrolog.TextStyle.bold}=> {pyrolog.TextStyle.reset}')

# ask for the api hash, if it doesn't set
if config['api_hash'] == 'ask':
  logger.info('Введите {style.bold}{fore.red}API HASH{reset}. Получить можно здесь: https://my.telegram.org')
  config['api_hash'] = input(f' {pyrolog.TextColor.green}{pyrolog.TextStyle.bold}*{pyrolog.TextStyle.reset} {pyrolog.TextStyle.bold}=> {pyrolog.TextStyle.reset}')

# initialize client
app = pyrogram.Client(
  'deanonvoprosy',
  api_id=config['api_id'],
  api_hash=config['api_hash'],
)

####


async def try_get_user(uid: str) -> tuple[str, str, str]:
  try:
    u = await app.get_users(int(uid))
    fn = u.first_name
    ln = '' if u.last_name is None else f' {u.last_name}'            # last name can be empty
    nick = 'Неизвестно' if u.username is None else f'@{u.username}'  # username can be empty
  except:
    logger.error('Невозможно получить данные пользователя, ID: {}',  uid)
    fn = 'Неизвестно'
    ln = ''
    nick = 'Неизвестно'
  return fn, ln, nick


# deanon @anonimnye_voprosy_bot
async def deanon_1(app: pyrogram.Client, bot_nickname: str = 'ananimnye_voprosy_bot'):
  # main script code
  try:
    m: pyrogram.types.Message | None = None  # for the type-hints :)

    # iterate all the history with the bot
    async for m in app.get_chat_history(bot_nickname):

      # check if message is valid
      if m.text is None or m.reply_markup is None or not hasattr(m.reply_markup, 'inline_keyboard') or 'ответить' not in m.reply_markup.inline_keyboard[0][0].text.lower():
        continue

      msg_text = ' '.join(m.text.split('\n\n')[1:])                           # get message text
      uid = m.reply_markup.inline_keyboard[0][0].callback_data.split(':')[1]  # get user id, that wrote this message

      # check if the message from is bot or bot admin
      if uid == 'bot':
        fn = 'Бот'
        ln = ' (сообщение написано от имени бота)'
        nick = '@anonimnye_voprosy_bot'
      elif uid == BOT_ADMIN_ID:
        fn = 'Админ бота'
        ln = ' (сообщение написано от имени админа бота)'
        nick = 'Неизвестно'
      else:
        # try to get information about the user
        fn, ln, nick = await try_get_user(uid)

      # print collected information
      logger.info('Сообщение: {}', msg_text)
      logger.info('Автор:     {}{}', fn, ln)
      logger.info('{style.bold}ID:        {}{reset}', uid)
      logger.info('Ник:       {}', nick)
      print()

  except Exception as e:
    logger.exception('Ошибка во время работы скрипта.', exc=e)
    return


# deanon @questianonbot
async def deanon_2(app: pyrogram.Client):
  # main script code
  try:
    m: pyrogram.types.Message | None = None  # for the type-hints :)

    # iterate all the history with the bot
    async for m in app.get_chat_history('questianonbot'):

      # check if message is valid
      if m.text is None or m.reply_markup is None or not hasattr(m.reply_markup, 'inline_keyboard') or m.reply_markup.inline_keyboard[0][0].text != 'Ответить анонимно':
        continue

      msg_text = ' '.join(m.text.split('\n \n')[1:])                                  # get message text
      uid = json.loads(m.reply_markup.inline_keyboard[0][0].callback_data)['value']  # get user id, that wrote this message

      # try to get information about the user
      fn, ln, nick = await try_get_user(uid)

      # print collected information
      logger.info('Сообщение: {}', msg_text)
      logger.info('Автор:     {}{}', fn, ln)
      logger.info('{style.bold}ID:        {}{reset}', uid)
      logger.info('Ник:       {}', nick)
      print()

  except Exception as e:
    logger.exception('Ошибка во время работы скрипта.', exc=e)
    return

####

choices = ['1', '2', '3']

# choice a bot
logger.info('{style.bold}Выберете бота которым вы пользуетесь:{reset}')
logger.info('  {style.bold}{fore.red}1. {reset} @anonimnye_voprosy_bot')
logger.info('  {style.bold}{fore.red}2. {reset} @anonka_ru_bot')
logger.info('  {style.bold}{fore.red}3. {reset} @questianonbot')

while 1:
  bot = input(f' {pyrolog.TextColor.green}{pyrolog.TextStyle.bold}*{pyrolog.TextStyle.reset} {pyrolog.TextStyle.bold}=> {pyrolog.TextStyle.reset}')
  # check if bot number is correct
  if bot not in choices:
    logger.error('{fore.lightred}Вы должны ввести одну из предоставленных цифер!')
    continue
  break


async def main():
  async with app:
    # save configuration file (if the asked credentials are work)
    CONFIG_PATH.write_text(toml.dumps(config))

    if bot == '1':
      await deanon_1(app)
    elif bot == '2':
      await deanon_1(app, 'anonka_ru_bot')
    elif bot == '3':
      await deanon_2(app)

# try to run a script
try:
  app.run(main())
except Exception as e:
  logger.exception('Ошибка во время запуска клиента.', exc=e)
  sys.exit()
