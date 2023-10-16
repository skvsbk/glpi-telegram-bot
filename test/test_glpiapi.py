import os
import pytest
from app.utils import glpiapi, glpidb
from app.config import Config


class TestGlpiApiGet:
    def test_glpi_init(self):
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
    def test_get_location(self, search_name, result):
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
    def test_get_equipment(self, search_name, result):
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
    def test_get_equipment_or_location(self, search_name, theme, result):
        user_creds = glpidb.get_user_credentials('+7 (111) 111-11-11')
        user = glpiapi.User(user_id=user_creds.get('id'),
                            token=user_creds.get('user_token'),
                            locations_name=user_creds.get('locations_name'))
        glpi = glpiapi.GLPI(url=Config.URL_GLPI, user_obj=user)
        location_id = glpi._get_equipment_or_location(search_name, theme)
        print(location_id)
        assert location_id == result


class TestGlpiApiTicketPost:
    tickets_id = []
    glpi_obj = []

    @pytest.mark.parametrize('ticket_obj, result',
                             [({'name': 'Оборудование Р-1.038', 'content': 'test', 'category_id': 1, 'urgency_id': 1},
                               'test'),
                              ({'name': 'Помещение 1.011', 'content': 'test', 'category_id': 1, 'urgency_id': 1},
                               'test'),
                              ]
                             )
    def test_create_ticket(self, ticket_obj, result):
        user_creds = glpidb.get_user_credentials('+7 (111) 111-11-11')
        user = glpiapi.User(user_id=user_creds.get('id'),
                            token=user_creds.get('user_token'),
                            locations_name=user_creds.get('locations_name'))
        glpi = glpiapi.GLPI(url=Config.URL_GLPI, user_obj=user)

        ticket = glpiapi.Ticket()
        for item, key in ticket_obj.items():
            ticket.__dict__[item] = key

        glpi.ticket = ticket

        ticket_id = glpi.create_ticket()
        self.tickets_id.append(ticket_id)
        self.glpi_obj.append(glpi)

        assert ticket_id > 0

    def test_get_created_ticket(self):
        for i, ticket_id in enumerate(self.tickets_id):
            url = f'{self.glpi_obj[i].url}/Ticket/{ticket_id}'
            headers = self.glpi_obj[i].headers
            response = glpiapi.GlpiApiRequest.request(headers=headers, url=url, payload=None, request_type='get')
            assert response.json().get('id') == ticket_id


class TestGlpiApiProjectPost:
    projects_id = []
    glpi_obj = []

    @pytest.mark.parametrize('project_obj, result',
                             [({'name': 'Проект Тест', 'content': 'test'}, 'test'),
                              # ({'name': 'Помещение 1.011', 'content': 'test', 'category_id': 1, 'urgency_id': 1},
                              #  'test'),
                              ]
                             )
    def test_create_project(self, project_obj, result):
        user_creds = glpidb.get_user_credentials('+7 (111) 111-11-11')
        user = glpiapi.User(user_id=user_creds.get('id'),
                            token=user_creds.get('user_token'),
                            locations_name=user_creds.get('locations_name'))
        glpi = glpiapi.GLPI(url=Config.URL_GLPI, user_obj=user)

        project = glpiapi.Project()
        for item, key in project_obj.items():
            project.__dict__[item] = key

        glpi.project = project

        project_id = glpi.create_project()
        self.projects_id.append(project_id)
        self.glpi_obj.append(glpi)

        assert project_id > 0

    def test_get_created_project(self):
        for i, project_id in enumerate(self.projects_id):
            url = f'{self.glpi_obj[i].url}/Project/{project_id}'
            headers = self.glpi_obj[i].headers
            response = glpiapi.GlpiApiRequest.request(headers=headers, url=url, payload=None, request_type='get')
            assert response.json().get('id') == project_id


class TestUploadDoc:
    def test_upload_file(self):
        user_creds = glpidb.get_user_credentials('+7 (111) 111-11-11')
        user = glpiapi.User(user_id=user_creds.get('id'),
                            token=user_creds.get('user_token'),
                            locations_name=user_creds.get('locations_name'))
        glpi = glpiapi.GLPI(url=Config.URL_GLPI, user_obj=user)

        doc_name = F"Документ Тест"
        filename = 'test_file.doc'
        with open(Config.FILE_PATH+'/' + filename, 'w') as file:
            file.write('test')

        doc_id = glpi.upload_doc(Config.FILE_PATH, filename, doc_name)
        assert doc_id > 0
        os.remove(Config.FILE_PATH+'/' + filename)
