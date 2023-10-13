import pytest
from app.utils import glpiapi, glpidb
from app.config import Config
import types





def test_glpi_init():
    user_creds = glpidb.get_user_credentials('+7 (111) 111-11-11')
    user = glpiapi.User(user_id=user_creds.get('id'),
                        token=user_creds.get('user_token'),
                        locations_name=user_creds.get('locations_name'))
    glpi = glpiapi.GLPI(url=Config.URL_GLPI, user_obj=user)
    print(glpi.session)
    assert isinstance(glpi.session, str)


@pytest.mark.parametrize('search_name, result',
                         [('1.011', 17),
                          ('12wqw', None)
                          ]
                         )
def test_get_location(search_name, result):
    user_creds = glpidb.get_user_credentials('+7 (111) 111-11-11')
    user = glpiapi.User(user_id=user_creds.get('id'),
                        token=user_creds.get('user_token'),
                        locations_name=user_creds.get('locations_name'))
    glpi = glpiapi.GLPI(url=Config.URL_GLPI, user_obj=user)
    location_id = glpi._get_location_id(search_name)
    print(location_id)
    assert location_id == result


@pytest.mark.parametrize('search_name, result',
                         [
                             ('Р-1.038', {'equipment_id': 32, 'locations_id': 14}),
                             ('12qwedw', None)
                         ]
                         )
def test_get_equipment(search_name, result):
    user_creds = glpidb.get_user_credentials('+7 (111) 111-11-11')
    user = glpiapi.User(user_id=user_creds.get('id'),
                        token=user_creds.get('user_token'),
                        locations_name=user_creds.get('locations_name'))
    glpi = glpiapi.GLPI(url=Config.URL_GLPI, user_obj=user)
    location_id = glpi._get_equipment_id(search_name)
    print(location_id)
    assert location_id == result

@pytest.mark.parametrize('search_name, theme, result',
                         [
                             ('Р-1.038', 'Оборудование', {'equipment_id': 32, 'locations_id': 14}),
                             ('12wefqw', 'Оборудование', {'equipment_id': None, 'locations_id': 0}),
                             ('1.011', 'Помещение', {'equipment_id': None, 'locations_id': 17}),
                             ('12wefqw', 'Помещение', {'equipment_id': None, 'locations_id': 0})
                         ]
                         )
def test_equipment_or_location(search_name, theme, result):
    user_creds = glpidb.get_user_credentials('+7 (111) 111-11-11')
    user = glpiapi.User(user_id=user_creds.get('id'),
                        token=user_creds.get('user_token'),
                        locations_name=user_creds.get('locations_name'))
    glpi = glpiapi.GLPI(url=Config.URL_GLPI, user_obj=user)
    location_id = glpi._get_equipment_or_location(search_name, theme)
    print(location_id)
    assert location_id == result
