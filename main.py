from create_bot import bot, dp
from handlers import client, admin, other

# client.regster_handlers_client(dp)
other.regster_handlers_other(dp)

if __name__ == '__main__':
    dp.run_polling(bot)
