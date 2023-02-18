import sqlite3

database = sqlite3.connect('./config_data/bot.sqlite')
cursor = database.cursor()


def add_user(user_id: int, user_dict: dict):
    cursor.execute(f"SELECT id FROM users WHERE id={user_id}")
    user = cursor.fetchone()
    if not user:
        cursor.execute(
            f'INSERT INTO users VALUES(?,?,?,?)',
            (user_id, user_dict[user_id]['name'], user_dict[user_id]['age'], user_dict[user_id]['gender'])
        )
        database.commit()
    else:
        pass

def drop_user_from_users(user_id: int) -> None:
    cursor.execute(
        f'DELETE FROM users WHERE id={user_id}'
    )
    database.commit()


def user_check(user_id: int) -> bool:
    cursor.execute(f"SELECT id FROM users WHERE id={user_id}")
    user = cursor.fetchone()
    if user is None:
        return False
    return True


def get_user_name(user_id: int) -> str:
    cursor.execute(
        f'SELECT name FROM users WHERE id={user_id}'
    )
    return cursor.fetchone()[0]


def get_user_age(user_id: int) -> int:
    cursor.execute(
        f'SELECT age FROM users WHERE id={user_id}'
    )
    return cursor.fetchone()[0]


def get_user_gender(user_id: int) -> str:
    cursor.execute(
        f'SELECT gender FROM users WHERE id={user_id}'
    )
    return cursor.fetchone()[0]