#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import re
import json

from os import listdir
from os.path import isfile, join
from jsonschema import validate
from jsonschema import ValidationError


def upload_schemas_to_db(directory, dbservice):
    schemas = [f for f in listdir(directory) if isfile(join(directory, f)) and f.endswith('.schema')]

    for schema in schemas:
        schemaText = ''
        with open(directory + '/' + schema, 'r') as schemaFile:
            schemaText = schemaFile.read().replace('\n', ' ')
            schemaText = re.sub(r"\s+", " ", schemaText)

        jsonSample = ''
        with open(directory + '/' + schema[:7] + '-sample.json', 'r') as sampleFile:
            jsonSample = sampleFile.read().replace('\n', ' ')
            jsonSample = re.sub(r"\s+", " ", jsonSample)

        try:
            validate(json.loads(jsonSample), json.loads(schemaText))
        except ValidationError as err:
            logging.error(u'Error while validating ' + directory + '/' + schema)
            raise err

        dbservice.update("""
                INSERT INTO validation.JSON_SCHEMA (NAME, BODY) 
                VALUES ('{0}', '{1}')
                ON CONFLICT (NAME) DO UPDATE SET BODY = excluded.BODY
                """.format(schema[:7].lower(), schemaText))


class ValidationService:
    def __init__(self, dbservice):
        self.dbservice = dbservice
        self.schemas = {}

    def load_schemas(self):
        self.dbservice.query("SELECT NAME, BODY FROM validation.JSON_SCHEMA;",
            lambda row: self.schemas.__setitem__(row[0], row[1]))
        logging.debug(u'Loaded schemas from db ' + str(self.schemas.keys()))

    def validate_json(self, schema_name, jsonText):
        validate(json.loads(jsonText), json.loads(self.schemas[schema_name]))