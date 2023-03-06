import sqlite3

database = sqlite3.connect('./config_data/bot.sqlite')
database.row_factory = sqlite3.Row
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

        cursor.execute(
            f'INSERT INTO obj_detections VALUES(?,{"?," * 79}?)',
            (user_id,) + (0,) * 80
        )
        database.commit()
    else:
        pass


def add_detections(user_id: int, detecion_dict: dict) -> None:
    keys = detecion_dict.keys()
    for key in keys:
        cursor.execute(
            f'UPDATE obj_detections SET {key} = {key}+{detecion_dict[key]} WHERE id={user_id}'
        )
        database.commit()


def drop_user_from_users(user_id: int) -> None:
    cursor.execute(
        f'DELETE FROM users WHERE id={user_id}'
    )
    database.commit()


def get_detection_info(user_id: int) -> dict:
    cursor.execute(f'SELECT * FROM obj_detections WHERE id={user_id}')
    result = [dict(row) for row in cursor.fetchall()][0]
    return result


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
