import logging
import pymysql
from app.config import Config


logger = logging.getLogger(__name__)
logger.setLevel('INFO')


def db_connetion():
    # DB credentials
    db_host = Config.DB_HOST
    db_name = Config.DB_NAME
    db_user = Config.DB_USER
    db_pass = Config.DB_PASS

    # Connect to DB
    return pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_pass,
        db=db_name,
        cursorclass=pymysql.cursors.DictCursor)


def get_user_credentials(mobile):
    """
    :param mobile: search creteria
    :return: dictionary with user params
    """
    connection = db_connetion()
    user_creds = dict()
    try:
        with connection.cursor() as cursor:
            # """
            # SELECT glpi_users.id, api_token, firstname FROM glpi_users
            # WHERE mobile = "+7 (950) 014-93-24" AND is_active=1
            # """
            # query = f'SELECT glpi_users.id, api_token, firstname FROM glpi_users ' \
            #         f'WHERE mobile = "{mobile}" AND is_active=1'
            #
            # SELECT glpi_users.id, api_token, firstname, glpi_locations.name AS locations_name FROM glpi_users
            # JOIN glpi_locations ON glpi_users.locations_id = glpi_locations.id
            # WHERE mobile = "+7 (911) 009-65-76" AND is_active=1

            """
            SELECT glpi_users.id, api_token, firstname, glpi_locations.name AS locations_name,
            glpi_plugin_fields_usertelegramids.telegramidfield FROM glpi_users
            JOIN glpi_locations ON glpi_users.locations_id = glpi_locations.id
            LEFT JOIN glpi_plugin_fields_usertelegramids ON glpi_plugin_fields_usertelegramids.items_id = glpi_users.id
            WHERE mobile = "+7 (921) 855-13-15" AND is_active=1
            """

            query = (f'SELECT glpi_users.id, api_token, firstname, glpi_locations.name AS locations_name, '
                     f'glpi_plugin_fields_usertelegramids.telegramidfield AS telegramid '
                     f'FROM glpi_users JOIN glpi_locations ON glpi_users.locations_id = glpi_locations.id '
                     f'LEFT JOIN glpi_plugin_fields_usertelegramids '
                     f'ON glpi_plugin_fields_usertelegramids.items_id = glpi_users.id'
                     f' WHERE mobile = "{mobile}" AND is_active=1')

            cursor.execute(query)

            for row in cursor:
                user_creds['user_token'] = row.get('api_token')
                user_creds['id'] = row.get('id')
                user_creds['firstname'] = row.get('firstname')
                user_creds['locations_name'] = row.get('locations_name')
                user_creds['telegramid'] = row.get('telegramid')
    except:
        logger.warning('get_user_credentials() - error getting user_id for %s', str(mobile))
    finally:
        logger.info('the function get_user_credentials() is done for the mobile %s', str(mobile))
        connection.close()

    return user_creds


def put_telegramid_for_user(user_id, telegramid):

    connection = db_connetion()
    try:
        with connection.cursor() as cursor:
            # Check item with user_id in glpi_plugin_fields_usertelegramids
            query = f'SELECT id FROM glpi_plugin_fields_usertelegramids WHERE items_id = {user_id}'
            cursor.execute(query)
            fields_is = None
            for row in cursor:
                fields_is = row.get('id')

            if fields_is in ('', None):
                # this is a new
                """
                INSERT INTO glpi_plugin_fields_usertelegramids (items_id, telegramidfield) VALUES (149, 11223344)
                """
                query = f'INSERT INTO glpi_plugin_fields_usertelegramids (items_id, telegramidfield) VALUES (%s, %s)'
                cursor.execute(query, (user_id, telegramid))
                connection.commit()
            else:
                query = (f'UPDATE glpi_plugin_fields_usertelegramids '
                         f'SET telegramidfield = {telegramid} '
                         f'WHERE items_id = {user_id}')
                cursor.execute(query)
                connection.commit()

    except:
        logger.warning('put_telegramid_for_user() - error set TelegranID for user_id = %s', str(user_id))
    finally:
        logger.info('the function put_telegramid_for_user() is done for user_id %s', str(user_id))
        connection.close()


def get_location_id(location_name):
    connection = db_connetion()
    location_id = None
    try:
        with connection.cursor() as cursor:
            """
            SELECT * FROM glpi_locations WHERE name LIKE '%1.011%'
            """
            query = f"SELECT id FROM glpi_locations WHERE name LIKE '%{location_name}%'"
            cursor.execute(query)
            for row in cursor:
                location_id = row.get('id')
    except:
        logger.warning('get_location_id() - error getting location_id %s', location_name)
    finally:
        logger.info('the get_location_id() is done for location_id %s', location_name)
        connection.close()
    return location_id


def get_equipment_id(equipment_name):
    connection = db_connetion()
    equipment_id = None
    try:
        with connection.cursor() as cursor:
            """
            SELECT id, locations_id FROM glpi_peripherals WHERE name LIKE '%Р-1.038%'
            """
            query = f"SELECT id, locations_id FROM glpi_peripherals WHERE name LIKE '%{equipment_name}%'"
            cursor.execute(query)
            for row in cursor:
                equipment_id = {'id': row.get('id'),
                                'locations_id': row.get('locations_id')}
    except:
        logger.warning('get_equipment_id() - error getting equipment_id %s', equipment_name)
    finally:
        logger.info('the get_equipment_id() is done for equipment_id %s', equipment_name)
        connection.close()
    return equipment_id


def query_tickets_init_atwork(user_id):
    """
    SELECT T1.id, T1.date, T1.name, T1.content, T1.status,
    CONCAT(U1.realname, ' ', U1.firstname) AS handler_name
    FROM glpi_tickets T1
    JOIN glpi_tickets_users TU1 ON TU1.tickets_id = T1.id
    JOIN glpi_users U1 ON U1.id = TU1.users_id
    WHERE T1.id IN (SELECT glpi_tickets_users.tickets_id FROM glpi_tickets_users
    WHERE glpi_tickets_users.users_id = 149
    AND glpi_tickets_users.type = 1) AND T1.status IN (1, 2, 3, 4) AND T1.is_deleted = 0 AND TU1.type = 2
    """
    return (f'SELECT T1.id, T1.date, T1.name, T1.content, T1.status, '
            f'CONCAT(U1.realname, " ", U1.firstname) AS user_name '
            f'FROM glpi_tickets T1 '
            f'JOIN glpi_tickets_users TU1 ON TU1.tickets_id = T1.id '
            f'JOIN glpi_users U1 ON U1.id = TU1.users_id '
            f'WHERE T1.id IN '
            f'(SELECT glpi_tickets_users.tickets_id '
            f'FROM glpi_tickets_users '
            f'WHERE glpi_tickets_users.users_id = {user_id} '
            f'AND glpi_tickets_users.type = 1) '
            f'AND T1.status IN (1, 2, 3, 4) '
            f'AND T1.is_deleted = 0 AND TU1.type = 2')


def query_tickets_executer_atwork(user_id):
    """
     SELECT T1.id, T1.date, T1.name, T1.content, T1.status,
     CONCAT(U1.realname, ' ', U1.firstname) AS init_name
     FROM glpi_tickets T1
     JOIN glpi_tickets_users TU1 ON TU1.tickets_id = T1.id
     JOIN glpi_users U1 ON U1.id = TU1.users_id
     WHERE T1.id IN (SELECT glpi_tickets_users.tickets_id FROM glpi_tickets_users
     WHERE glpi_tickets_users.users_id = 149
     AND glpi_tickets_users.type = 1) AND T1.status IN (1, 2, 3, 4) AND T1.is_deleted = 0 AND TU1.type = 2
     """
    return (f'SELECT T1.id, T1.date, T1.name, T1.content, T1.status, '
            f'CONCAT(U1.realname, " ", U1.firstname) AS user_name '
            f'FROM glpi_tickets T1 '
            f'JOIN glpi_tickets_users TU1 ON TU1.tickets_id = T1.id '
            f'JOIN glpi_users U1 ON U1.id = TU1.users_id '
            f'WHERE T1.id IN '
            f'(SELECT glpi_tickets_users.tickets_id '
            f'FROM glpi_tickets_users '
            f'WHERE glpi_tickets_users.users_id = {user_id} '
            f'AND glpi_tickets_users.type = 2) '
            f'AND T1.status IN (1, 2, 3, 4) '
            f'AND T1.is_deleted = 0 AND TU1.type = 1')


def query_solved_tickets(user_id):
    """
    SELECT T1.id, T1.date, T1.name, T1.content, T1.status,
    CONCAT(U1.realname, ' ', U1.firstname) AS handler_name
    FROM glpi_tickets T1
    JOIN glpi_tickets_users TU1 ON TU1.tickets_id = T1.id
    JOIN glpi_users U1 ON U1.id = TU1.users_id
    WHERE T1.id IN (SELECT glpi_tickets_users.tickets_id FROM glpi_tickets_users
    WHERE glpi_tickets_users.users_id = 149
    AND glpi_tickets_users.type = 1) AND T1.status = 5 AND T1.is_deleted = 0 AND TU1.type = 2
    """
    return (f'SELECT T1.id, T1.date, T1.name, T1.content, T1.status, '
            f'CONCAT(U1.realname, " ", U1.firstname) AS user_name '
            f'FROM glpi_tickets T1 '
            f'JOIN glpi_tickets_users TU1 ON TU1.tickets_id = T1.id '
            f'JOIN glpi_users U1 ON U1.id = TU1.users_id '
            f'WHERE T1.id IN '
            f'(SELECT glpi_tickets_users.tickets_id '
            f'FROM glpi_tickets_users '
            f'WHERE glpi_tickets_users.users_id = {user_id} '
            f'AND glpi_tickets_users.type = 1) '
            f'AND T1.status = 5 '
            f'AND T1.is_deleted = 0 AND TU1.type = 2')


def get_tickets(query_string):
    connection = db_connetion()
    tickets = {}
    try:
        with connection.cursor() as cursor:
            cursor.execute(query_string)
            for row in cursor:
                ticket_id = row.get('id')
                tickets.update({ticket_id: {}})
                tickets[ticket_id].update({'date': row.get('date')})
                tickets[ticket_id].update({'name': row.get('name')})
                tickets[ticket_id].update({'content': row.get('content').replace('&lt;p&gt;', '').
                                          replace('&lt;/p&gt;', ' ')})
                tickets[ticket_id].update({'status': Config.TICKET_STATUS[row.get('status')]})
                tickets[ticket_id].update({'user_name': row.get('user_name')})
    except Exception as e:
        logger.warning('get_tickets() - error getting tickets')
        logger.warning('get_tickets() - error: %s', e)
    finally:
        logger.info('the get_tickets() is done for user_id')
        connection.close()
    return tickets


if __name__ == '__main__':
    print('glpidb module')
    phone_for_send = "+7 (911) 111-11-11"

    user_c = get_user_credentials(phone_for_send)
    print(user_c)
    from glpiapi import User, GLPI
    user = User(user_id=user_c.get('id'),
                token=user_c.get('user_token'),
                locations_name=user_c.get('locations_name'))
    glpi = GLPI(url=Config.URL_GLPI, user=user)
    print(user.__dict__)
    print(glpi.__dict__)
