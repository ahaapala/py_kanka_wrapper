from py_kanka_wrapper.kanka_wrapper import kanka_wrapper
import os
from pytest import fixture
import pytest as pytest

class TestKankaWrapper:

    @fixture
    def wrapper(self,mocker):
      mocker.patch('requests.get',return_value='{"data":[{"name":"Test Campaign","id":"12345"}]}')
      token = 'NOTAREALTOKENCAUSETHESEAREUNITTESTS'
      
      return kanka_wrapper(token,'Test Campaign')  

    def test_set_campaign(self, wrapper,mocker):
        mocker.patch('requests.get',return_value='{"data":[{"name":"Test Campaign 1","id":"12345"}]}')
        wrapper.set_campaign('Test Campaign 1')
        assert wrapper.campaign_id == 12345

    def test_is_valid_entity_type(self,wrapper):
        is_valid = wrapper.is_valid_entity_type('Characters')
        assert is_valid

        is_valid = wrapper.is_valid_entity_type('Not a valid type')
        assert not is_valid

    def test_check_entity(self,wrapper, mocker):
        # Test if you pass it an int
        entity_id = wrapper.check_entity('Characters',123456)
        assert entity_id == 123456
        
        # Test if we pass it an entity name or string
        mocker.patch('requests.get', return_value='{"data":[{"name":"Test Entity","entity_id":"123456"}]}')
        entity_id = wrapper.check_entity('Characters','Test Entity')
        assert entity_id == 123456

    def test_check_entity_with_bad_type(self, wrapper):
        # Test if we pass an invalid entity type (raises an exception)
        with pytest.raises(Exception,match='get_entities()'):
            wrapper.check_entity('Bad Entity Type','12345')

    def test_check_entity_with_bad_value(self,wrapper):
        # Test if we pass an unexpected entity value
        with pytest.raises(Exception):
            wrapper.check_entity('Characters',{'This dict':'should be an exception'})
        

    def test_check_attribute(self, wrapper, mocker):
        mocker.patch('requests.get', side_effect = ['{"data":[{"name": "Test Entity","entity_id": 123456 }]}',
                                                    '{"data":[{"name": "Test Attribute","id": 1234567 }]}'])
        attribute_id = wrapper.check_attribute('Characters','Test Entity','Test Attribute')
        assert attribute_id == 1234567

    def test_get_campaign_id(self, wrapper, mocker):
        mocker.patch('requests.get', return_value='{"data":[{"name":"Test Campaign 2","id": 123456 }]}')
        campaign_id = wrapper.get_campaign_id('Test Campaign 2')
        assert campaign_id == 123456

    def test_get_entity(self, wrapper, mocker):
        mocker.patch('requests.get', side_effect=['{"data":[{"name": "Test Character", "entity_id": 1234567 }]}',
                                                 '{"data":[{"name": "Test Character", "entity_id": 1234567 }]}'])
        entity = wrapper.get_entity('Characters','Test Character')
        assert isinstance(entity,dict)
        assert entity['data'][0]['entity_id'] == 1234567 and entity['data'][0]['name'] == "Test Character"

    def test_get_entity_id(self,wrapper,mocker):
        mocker.patch('requests.get', return_value='{"data":[{"name":"Test Location","entity_id": 123456}]}')
        entity_id = wrapper.get_entity_id('Locations','Test Location')
        assert isinstance(entity_id,int)
        assert entity_id == 123456

    def test_get_entities(self,wrapper,mocker):
        mocker.patch('requests.get',return_value='{"data":[{"name":"Location 1","id": 123456},{"name":"Location 2", "id": 123457},{"name":"Location 3","id": 123458}]}')
        entities = wrapper.get_entities('Locations')

        assert isinstance(entities['data'], list)
        for entity in entities['data']:
            assert isinstance(entity['name'],str)
            assert isinstance(entity['id'],int)
            assert "Location" in entity['name']

    def test_get_attribute(self,wrapper,mocker):
        """
            TODO:
            - This can throw exceptions so it should have tests for them as well
            - Could also assert for full data-structure being returned from api
        """
        mocker.patch('requests.get',side_effect=['{"data": [{"name":"Test Character","entity_id": 12345}]}',
                                                 '{"data": [{"name": "Test Attribute","id": 123456 }]}',
                                                 '{"data": [{"name": "Test Attribute","id": 123456, "value": "20"}]}'])
        attribute = wrapper.get_attribute('Characters','Test Character','Test Attribute')
        assert isinstance(attribute,dict)
        assert attribute['data'][0]['value'] == "20"

    def test_get_attributes(self,wrapper,mocker):
        mocker.patch('requests.get', return_value='{"data":[{"name":"attribute 1","value":"val 1"},{"name":"attribute 2","value":"val 2"},{"name":"attribute 3","value":"val 3"}]}')
        attributes = wrapper.get_attributes(123456)
        assert isinstance(attributes['data'],list)
        for attribute in attributes['data']:
            assert isinstance(attribute['name'],str)
            assert isinstance(attribute['value'],str)


    def test_get_attribute_id(self,wrapper,mocker):
        mocker.patch('requests.get',side_effect=['{"data":[{"name":"Test Character","entity_id":123456}]}','{"data":[{"name":"Test Attribute","id":1234,"value": ""}]}'])
        attribute_id = wrapper.get_attribute_id('Characters','Test Character','Test Attribute')
        assert isinstance(attribute_id,int)
        assert attribute_id == 1234
        
    def test_update_attribute(self,wrapper,mocker):
        mocker.patch('requests.get', return_value='{"data": [{"name": "Test Character","entity_id": 12345}]}')
        mocker.patch('requests.put', return_value='{"data":{"name": "Test Attribute", "value": "Test Value"}}')
        response = wrapper.update_attribute('Characters','Test Character','Test Attribute','Test Value')
        assert isinstance(response,dict)
        assert response['data']['value'] == 'Test Value'
        
    def test_update_attributes(self,wrapper,mocker):
        mocker.patch('requests.get', side_effect=['{"data": [{"name": "Test Character","entity_id": 12345}]}',
                                                  '{"data": [{"name": "Test Character","entity_id": 12345}]}',
                                                  '{"data": [{"name": "Test Character","entity_id": 12345}]}'])
        mocker.patch('requests.put', side_effect=['{"data":{"name": "Test Attribute 1", "value": "Test Value 1"}}',
                                                  '{"data":{"name": "Test Attribute 2", "value": "Test Value 2"}}',
                                                  '{"data":{"name": "Test Attribute 3", "value": "Test Value 3"}}'])
        attribute_updates = {'Test Attribute 1': 'Test Value 1',
                             'Test Attribute 2': 'Test Value 2',
                             'Test Attribute 3': 'Test Value 3'}

        generator = wrapper.update_attributes('Characters','Test Character',attribute_updates)

        for response in generator:
            assert isinstance(response,dict)
            assert 'Test Attribute' in response['data']['name']
            assert 'Test Value' in response['data']['value']

    def test_update_entity(self,wrapper,mocker):
        mocker.patch('requests.put', return_value='{"data": {"title":"Test Title"}}')
        entity_data = {'name': 'Test Character', 'entity_id': 123456, 'title': 'Test Title'}
        response = wrapper.update_entity('Characters','Test Character', entity_data)
        assert isinstance(response,dict)
        assert response['data']['title'] == 'Test Title'

    def test_update_entities(self,wrapper,mocker):
        mocker.patch('requests.put', side_effect=['{"data":{"name": "Test Entity 1", "value": "Test Value 1"}}',
                                                  '{"data":{"name": "Test Entity 2", "value": "Test Value 2"}}',
                                                  '{"data":{"name": "Test Entity 3", "value": "Test Value 3"}}'])

        entities = {'entity_name_1':{'name': 'Test Entity 1','value': 'Test','title': 'Test Title'},
                    'entity_name_2':{'name': 'Test Entity 2','value': 'Test','title': 'Test Title 2'}}        
        generator = wrapper.update_entities('Characters',entities)
        for response in generator:
            assert isinstance(response,dict)
            assert 'Test Value' in response['data']['value']

    def test_create_attribute(self,wrapper,mocker):
        mocker.patch('requests.get',return_value='{"data": [{"name": "Test Location 1","entity_id": 12345}]}')
        mocker.patch('requests.post',return_value='{"data":{"name":"Test Attribute","value":"Test Value 1"}}')
        response = wrapper.create_attribute('Locations','Test Location 1','Test Attribute 1','Test Value 1')
        assert isinstance(response,dict)
        assert response['data']['name'] == "Test Attribute"

    def test_create_entity(self,wrapper,mocker):
        mocker.patch('requests.post',return_value='{"data":[{"name": "Test Location","type": "Test","image_url":"https://test.com"}]}')
        data = {'name': 'Test Location','type':'Test','image_url':'https://test.com'}
        response = wrapper.create_entity('Locations','New Location 1',data)
        assert isinstance(response,dict)
        assert response['data'][0]['type'] == 'Test'

    def test_delete_attribute(self,wrapper,mocker):
        mocker.patch('requests.get',side_effect=['{"data":[{"name":"Test Entity","entity_id":12345}]}',
                                                 '{"data":[{"name":"Test Attribute","id":54321}]}'])
        mocker.patch('requests.delete',return_value='{"data":[{"name":"Test Attribute"}]}')
        response = wrapper.delete_attribute('Characters', 'Test Entity', 'Test Attribute')
        assert isinstance(response,dict)

    def test_delete_entity(self,wrapper,mocker):
        mocker.patch('requests.get',return_value='{"data":[{"name":"Test Entity","entity_id":12345}]}')
        mocker.patch('requests.delete',return_value='{"data":[{"name":"Test Entity","entity_id":12345}]}')
        response = wrapper.delete_entity('Notes','Test Note')
        assert isinstance(response,dict)

    def test_search(self,wrapper,mocker):
        mocker.patch('requests.get',return_value='{"data":[{"name":"Test Results","type":"Test"}]}')
        response = wrapper.search('Test Term')
        assert isinstance(response,dict)
        assert response['data'][0]['name'] == 'Test Results'
        assert response['data'][0]['type'] == 'Test'
