import requests
import requests_cache
import json

"""
   NOTES:
   This class should have very little to do with formatting the results of the queries.  That should be left to the calling logic since display format is usually dependant on context.
   Not all functionality of the api is addressed or leveraged in this class.  I want to establish a working minimal product before filling in the rest and as it is currently meets my needs.
   Code and trying to utilize rolls via an api is awkward.
"""


class kanka_wrapper:

    base_url = 'https://kanka.io/api/1.0/'

    VALID_ENTITY_TYPES = ['characters',
                          'locations',
                          'families',
                          'organizations',
                          'items',
                          'notes',
                          'events',
                          'calendars',
                          'races'
                          'quests',
                          'journals',
                          'tags',
                          'conversations']

    def __init__(self, token, campaign):
        self.kanka_token = token
        self.headers = {'Authorization': 'Bearer ' + self.kanka_token,
                        'Accept': 'application/json'}
        self.set_campaign(campaign)
        self.current_entity = {}
        requests_cache.install_cache(campaign + '_cache', backend='memory', expire_after=300)

    def set_campaign(self, campaign):
        self.campaign = campaign
        self.campaign_id = self.get_campaign_id(self.campaign)

    def is_valid_entity_type(self, entity_type):
        print('******* ' + entity_type.lower())
        if entity_type.lower() in self.VALID_ENTITY_TYPES:
            return True
        return False

    def check_entity(self, entity_type, entity):
        """
            Helper method to support referring to entities by name or by id
        """
        if isinstance(entity, str):
            """
                This is an entity name so we have to look up the id.  This should now translucently cache any requests via
                requests_cache.
            """
            return self.get_entity_id(entity_type, entity)

        elif isinstance(entity, int):
            # This is an entity id and we can use it as is
            return entity
        else:
            raise(Exception('Invalid entity identifier in check_entity()'))

    def check_attribute(self, entity_type, entity, attribute):
        """
            Helper method to handling attributes referred by name or id
        """
        if isinstance(attribute, str):
            """
                This is an attribute name so we have to look up the id.  All requests should now be cached via the requests_cache lib.
            """
            return self.get_attribute_id(entity_type, entity, attribute)

        elif isinstance(attribute, int):
            # This is an entity id and we can use it as is
            return attribute
        else:
            raise(Exception('Invalid attribute identifier in check_attribute()'))

    """
        Remote getters
    """
    def get_campaign_id(self, campaign_name):
        """
           Matches the first campaign matching the name
        """
        url = self.base_url + '/campaigns'
        response = requests.get(url, headers=self.headers)

        for campaign in json.loads(response)['data']:
            if campaign['name'] == campaign_name:
                return int(campaign['id'])

        return None

    """
        Entities are any of the objects stored underneath a campaign, e.g. Characters, Locations, etc...
    """
    def get_entity(self, entity_type, entity):
        """
            Get an individual entity
        """
        if not self.is_valid_entity_type(entity_type):
            raise(Exception('Invalid entity type in get_entity()'))

        entity_id = self.check_entity(entity_type, entity)

        url = self.base_url + '/campaigns/' + str(self.campaign_id) + '/' + str(entity_type) + '/' + str(entity_id)
        return json.loads(requests.get(url, headers=self.headers))

    def get_entity_id(self, entity_type, entity_name):
        """
           entity_id is required for a lot of requests so it warrants its own
           method even if it's just wrapping get_entities and parsing for id
           - Right now this is an exact case-sensitive match.  This can be made more fuzzy
        """
        response = self.get_entities(entity_type)
        for entity in response['data']:
            if entity['name'] == entity_name:
                self.current_entity = entity
                return int(entity['entity_id'])

        return None

    def get_entities(self, entity_type):
        """
            Provide a valid entity type and it returns the results
        """
        if not self.is_valid_entity_type(entity_type):
            raise(Exception('Invalid entity type in get_entities()'))

        url = self.base_url + '/campaigns/' + str(self.campaign_id) + '/' + str(entity_type)

        return json.loads(requests.get(url, headers=self.headers))

    """
        Attributes are custom fields tacked onto an entity either via template
        or manual addition.  For my puproses these are game mechanics and things
        off of a character sheet.
        Notes:
        - I may just use the entity get call to retrieve attributes since they should be a subset of
        the entity.
    """
    def get_attribute(self, entity_type, entity, attribute):
        """
            Get a specific entity attribute
        """
        entity_id = self.check_entity(entity_type, entity)
        attribute_id = self.check_attribute(entity_type, entity_id, attribute)
        url = self.base_url + '/' + str(self.campaign_id) + '/entities/' + str(entity_id) + '/attributes/' + str(attribute_id)
        return json.loads(requests.get(url, headers=self.headers))

    def get_attributes(self, entity_id):
        """
            Get all attributes for an entity
        """
        url = self.base_url + '/campaign/' + str(self.campaign_id) + '/entities/' + str(entity_id) + '/attributes'
        return json.loads(requests.get(url, headers=self.headers))

    def get_attribute_id(self, entity_type, entity, attribute_name):
        """
            Like for entities, you need a numeric id to look up specific entries
        """
        entity_id = self.check_entity(entity_type, entity)
        attributes = self.get_attributes(entity_id)
        for attrib in attributes['data']:
            if attrib['name'] == attribute_name:
                return attrib['id']

        return None

    """
        Remote updaters
        - For already existing attributes
    """
    def update_attribute(self, entity_type, entity, attribute_name, value):
        """
            Just going with bare minimum for post body.  There's important other
            possible fields that should be supported.
        """
        entity_id = self.check_entity(entity_type, entity)
        attribute_id = self.check_attribute(entity_type, entity_id, attribute_name)

        body = {'name': attribute_name,       # attribute is required
                'value': value,
                'entity_id': entity_id}            # entity_id is required

        url = self.base_url + '/campaign/' + str(self.campaign_id) + '/entities/' + str(entity_id) + '/attributes/' + str(attribute_id)

        return json.loads(requests.put(url, data=body, headers=self.headers))

    def update_attributes(self, entity_type, entity, attributes_and_values):
        """
            Plural attribute setter.  Takes a dictionary e.g. {'attribute name': 'attribute value'}
        """
        for key, value in attributes_and_values.items():
            yield self.update_attribute(entity_type, entity, key, value)

    def update_entity(self, entity_type, entity, body):
        """
            Going to leave populating the post body for the calling logic
        """
        entity_id = self.check_entity(entity_type, entity)
        url = self.base_url + '/campaign/' + str(self.campaign_id) + '/' + str(entity_type) + '/' + str(entity_id)
        return json.loads(requests.put(url, headers=self.headers, data=body))

    def update_entities(self, entity_type, entities):
        """
            Plural entity setter.  Takes a dictionary e.g. {'entity name': {<entity body here>}}
        """
        for entity_name, entity_body in entities.items():
            yield self.update_entity(entity_type, entity_name, entity_body)

    """
        Remote creators
    """
    def create_attribute(self, entity_type, entity, attribute_name, value):
        entity_id = self.check_entity(entity_type, entity)
        body = {'name': attribute_name,
                'value': value,
                'entity_id': entity_id}

        url = self.base_url + '/campaign/' + str(self.campaign_id) + '/entities/' + str(entity_id) + '/attributes/'
        return json.loads(requests.post(url, data=body, headers=self.headers))

    def create_entity(self, entity_type, entity_name, body):
        url = self.base_url + '/campaign/' + str(self.campaign_id) + '/' + str(entity_type)
        return json.loads(requests.post(url, data=body, heades=self.headers))

    """
        Remote deleters
    """
    def delete_attribute(self, entity_type, entity, attribute):
        entity_id = self.check_entity(entity_type, entity)
        attribute_id = self.check_attribute(entity_type, entity_id, attribute)
        url = self.base_url + '/campaign/' + str(self.campaign_id) + '/entities/' + str(entity_id) + '/attributes/' + str(attribute_id)
        return json.loads(requests.delete(url, headers=self.headers))

    def delete_entity(self, entity_type, entity):
        entity_id = self.check_entity(entity_type, entity)
        url = self.base_url + '/campaign/' + str(self.campaign_id) + '/' + str(entity_type) + '/' + str(entity_id)
        return json.loads(requests.delete(url, headers=self.headers))

    """
        Search
    """
    def search(self, search_term):
        url = self.base_url + '/search/' + str(search_term)
        return json.loads(requests.get(url, headers=self.headers))
