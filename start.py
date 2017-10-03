#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, getopt
import logging
import configparser
import sys
import time

import validation
import templates

from templates import TemplateService
from validation import ValidationService
from dbutil import DBService
from queueutil import QueueService
from triggerapi import TriggerService


def main(argv):
    app_config = get_app_config(argv)
    config_logging(app_config['logFilename'])    
    logging.debug(u'Loaded app config ' + str(app_config))
    
    db_services = get_db_services(app_config['dbConfigFilename'])

    validation.upload_schemas_to_db(app_config['jsonSchemaDirectory'], db_services['DB-EMS-WRITER'])
    templates.upload_templates_to_db(app_config['templatesDirectory'], db_services['DB-EMS-WRITER'])

    template_service = TemplateService(db_services['DB-EMS-READER'])
    template_service.load_templates()
    validation_service = ValidationService(db_services['DB-EMS-READER'])
    validation_service.load_schemas()

    queue_service_config = load_queue_service_config(app_config['queueConfigFilename'])
    queue_service = QueueService(queue_service_config['CONNECTION'])
    queue_service.init()

    trigger_service = TriggerService(validation_service, queue_service, queue_service_config['TRIGGERS'])

    trigger_service.add_trigger('{ "type": "test", "sendTime": 3492734923, "tags": [ "my-tag1", "my-tag2" ], "data": { "my-property-1": "my-value-1", "my-property-2": "my-value-2" }}')
    time.sleep(5)




def print_usage():
    pass


default_config = {
    'logFilename': u'log.txt',
    'dbConfigFilename': u'pgsql.ini',
    'queueConfigFilename': u'kafka.ini',
    'jsonSchemaDirectory': u'json-schema',
    'templatesDirectory': u'templates'
}

def get_app_config(argv):
    app_config = default_config

    try:
        opts, args = getopt.getopt(argv,"hl:t:",["log-file=","templates-config-file="])
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print_usage()
            sys.exit()
        elif opt in ("-l", "--log-file"):
            app_config['logFilename'] = arg
        elif opt in ("-d", "--db-config-file"):
            app_config['dbConfigFilename'] = arg
        elif opt in ("-j", "--json-schema-directory"):
            app_config['jsonSchemaDirectory'] = arg
        elif opt in ("-t", "--templates-directory"):
            app_config['templatesDirectory'] = arg
        elif opt in ("-q", "--queue-config-file"):
            app_config['queueConfigFilename'] = arg

    return app_config


class LoggerWriter:
    def __init__(self, level):
        self.level = level

    def write(self, message):
        if message != '\n':
            self.level(message)

    def flush(self):
        self.level(sys.stderr)


def config_logging(filename):
    logging.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s', level = logging.DEBUG, filename = filename)
    sys.stdout = LoggerWriter(logging.info)
    sys.stderr = LoggerWriter(logging.warn)


def get_db_services(db_config_filename):
    config = configparser.ConfigParser()
    config.read(db_config_filename)
    result = {}
    for key, value in config.items():
        if key.startswith('DB-'):
            result[key] = DBService(value)
    return result


def load_queue_service_config(queue_config_filename):
    config = configparser.ConfigParser()
    config.read(queue_config_filename)
    return dict(config)


if __name__ == "__main__":
   main(sys.argv[1:])