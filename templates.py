#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

from os import listdir
from os.path import isfile, join
from jinja2 import Template


def upload_templates_to_db(directory, dbservice):
    templates = [f for f in listdir(directory) if isfile(join(directory, f)) and f.endswith('.jinja2')]

    for template in templates:
        with open(directory + '/' + template, 'r') as templateFile:
            body = templateFile.read()
            language = template.rpartition('.')[-1]
            name = template.rpartition('.')[0]
            status = 'active'
            if template.startswith('.'):
                name=name[1:]
                status='not active'
            dbservice.update("""
                INSERT INTO messages.TEMPLATE (NAME, BODY, LANGUAGE, STATUS) 
                VALUES ('{0}', '{1}', '{2}', '{3}')
                ON CONFLICT (NAME) DO UPDATE SET BODY = excluded.BODY, LANGUAGE = excluded.LANGUAGE, STATUS = excluded.STATUS
                """.format(name.lower(), body, language, status))


class TemplateService:
    def __init__(self, dbservice):
        self.dbservice = dbservice
        self.templates = {}

    def load_templates(self):
        self.dbservice.query("SELECT NAME, BODY FROM messages.V_TEMPLATE_ACTIVE WHERE LANGUAGE = 'jinja2';",
            lambda row: self.templates.__setitem__(row[0], Template(row[1])))
        logging.debug(u'Loaded templates from db ' + str(self.templates.keys()))

    def process_template(self, name, data):
        return self.templates[name].render(data)