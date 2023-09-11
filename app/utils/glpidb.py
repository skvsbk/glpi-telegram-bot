import datetime
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
    user_credentials = dict()
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

            query = f'SELECT glpi_users.id, api_token, firstname, glpi_locations.name AS locations_name, ' \
                    f'glpi_plugin_fields_usertelegramids.telegramidfield AS telegramid ' \
                    f'FROM glpi_users ' \
                    f'JOIN glpi_locations ON glpi_users.locations_id = glpi_locations.id ' \
                    f'LEFT JOIN glpi_plugin_fields_usertelegramids ' \
                    f'ON glpi_plugin_fields_usertelegramids.items_id = glpi_users.id ' \
                    f'WHERE mobile = "{mobile}" AND is_active=1'

            cursor.execute(query)

            for row in cursor:
                user_credentials['user_token'] = row['api_token']
                user_credentials['id'] = row['id']
                user_credentials['firstname'] = row['firstname']
                user_credentials['locations_name'] = row['locations_name']
                user_credentials['telegramid'] = row['telegramid']
    except:
        logger.warning('get_user_credentials() - error getting user_id for %s', str(mobile))
    finally:
        logger.info('the function get_user_credentials() is done for the mobile %s', str(mobile))
        connection.close()

    return user_credentials


def put_telegramid_for_user(user_id, telegramid):

    connection = db_connetion()
    try:
        with connection.cursor() as cursor:
            # Check item with user_id in glpi_plugin_fields_usertelegramids
            query = f'SELECT id FROM glpi_plugin_fields_usertelegramids WHERE items_id = {user_id}'
            cursor.execute(query)
            fields_is = None
            for row in cursor:
                fields_is = row['id']

            if fields_is in ('', None):
                # this is a new
                """
                INSERT INTO glpi_plugin_fields_usertelegramids (items_id, telegramidfield) VALUES (149, 11223344)
                """
                query = f'INSERT INTO glpi_plugin_fields_usertelegramids (items_id, telegramidfield) VALUES (%s, %s)'
                cursor.execute(query, (user_id, telegramid))
                connection.commit()
            else:
                query = f'UPDATE glpi_plugin_fields_usertelegramids SET telegramidfield = {telegramid} '\
                        f'WHERE items_id = {user_id}'
                cursor.execute(query)
                connection.commit()

    except:
        logger.warning('put_telegramid_for_user() - error set TelegranID for user_id = %s', str(user_id))
    finally:
        logger.info('the function put_telegramid_for_user() is done for user_id %s', str(user_id))
        connection.close()


def get_max_id(connection):
    """
    :return: max id from table glpi_documents_items for use it as tab_id in update_doc_item
    """
    # connection = db_connetion()
    try:
        with connection.cursor() as cursor:
            query = "SELECT MAX(id) FROM glpi_documents_items"
            cursor.execute(query)
            for row in cursor:
                max_id = row['MAX(id)']
    except:
        logger.warning('get_max_id() - error getting max_id')
    finally:
        logger.info('the function get_max_id() is done')
        connection.close()

    return max_id


def update_doc_item(documents_id, items_id, user_id):
    """
    :param documents_id: id uploaded image
    :param items_id: ticket id
    :param user_id: user id from get_user_credentials(mobile)
    :return:
    """
    connection = db_connetion()
    try:
        with connection.cursor() as cursor:
            # get max id
            query = "SELECT MAX(id) FROM glpi_documents_items"
            cursor.execute(query)
            for row in cursor:
                max_id = row['MAX(id)']
            tab_id = max_id+1

            # update glpi_documents_items
            date_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            columns = 'id, documents_id, items_id, itemtype, entities_id, is_recursive, date_mod, ' \
                      'users_id, timeline_position, date_creation'
            values = [(tab_id, documents_id, items_id, 'Ticket', 0, 1, f'{date_time}', user_id, 1, f'{date_time}')]
            query = f"INSERT INTO glpi_documents_items({columns}) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.executemany(query, values)
            connection.commit()
    except:
        logger.warning('update_doc_item() - error updating item_id %s', items_id)
    finally:
        logger.info('the update_doc_item() is done for item_id %s', items_id)
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
                location_id = row['id']
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
                equipment_id = {'id': row['id'], 'locations_id': row['locations_id']}
    except:
        logger.warning('get_equipment_id() - error getting equipment_id %s', equipment_name)
    finally:
        logger.info('the get_equipment_id() is done for equipment_id %s', equipment_name)
        connection.close()
    return equipment_id


if __name__ == '__main__':
    print('glpidb module')
    # u = get_user_credentials('+7 (921) 855-13-15')
    # u = get_user_credentials('+7 (981) 945-90-34')
    # u = get_user_credentials('+7 (950) 014-93-24')
    # u = get_location_id('1.011') #17
    u = get_equipment_id('Р-1.038') #32
    print(u)
