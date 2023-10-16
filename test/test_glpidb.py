import pytest
from app.utils import glpidb


class TestDBHardcore:
    @pytest.mark.parametrize('telephone_number, result',
                             [
                                 ('+7 (111) 111-11-11', ['user_token', 'id', 'firstname',
                                                         'locations_name', 'telegramid']),
                                 ('+7 (111) 111-11-00', [])
                             ]
                             )
    def test_get_user(self, telephone_number, result):
        user_creds = glpidb.get_user_credentials(telephone_number)
        print(user_creds)
        assert list(user_creds.keys()) == result

    @pytest.mark.parametrize('telephone_number, telegramid, result',
                             [
                                 ('+7 (111) 111-11-11', 1122334455, True),
                                 ('+7 (111) 111-11-00', 1122334455, False)
                             ]
                             )
    def test_put_telegramid(self, telephone_number, telegramid, result):
        user_creds = glpidb.get_user_credentials(telephone_number)
        user_id = user_creds.get('id')
        assert glpidb.put_telegramid_for_user(user_id, telegramid) == result

    @pytest.mark.parametrize('telephone_number, result',
                             [
                                 ('+7 (111) 111-11-11', '1122334455'),
                                 ('+7 (111) 111-11-00', None)
                             ]
                             )
    def test_get_telegramid(self, telephone_number, result):
        user_creds = glpidb.get_user_credentials(telephone_number)
        assert user_creds.get('telegramid') == result
