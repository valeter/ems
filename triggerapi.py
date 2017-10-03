#!/usr/bin/python
# -*- coding: utf-8 -*-

import jsonutil
import copy


class TriggerService:
    TRIGGER_SERVICE_TAG = "ems-trigger-service"

    def __init__(self, validation_service, queue_service, dbservice, triggers_topic_config):
        self.validation_service = validation_service
        self.queue_service = queue_service
        self.dbservice = dbservice
        self.topic = triggers_topic_config['topic']

    def add_trigger(self, req_json):
        self.validation_service.validate_json("trigger-request-add", req_json)
        trigger_request = jsonutil.parse_json(req_json)

        trigger = build_trigger(trigger_request)
        trigger.tags.append(TRIGGER_SERVICE_TAG)
        
        trig_json = jsonutil.to_json(trigger)
        self.validation_service.validate_json("trigger", json)
        
        self.queue_service.send(self.topic, trig_json)
        return trigger

    def build_trigger(self, request):
        trigger = copy.deepcopy(request)

        row = self.dbservice.query_single("""
            SELECT FILTER_NAMES, PROCESSOR_NAMES 
            FROM messages.V_TRIGGER_TYPE_ACTIVE WHERE NAME = {0};
            """.format(request.type))
        trigger.filters = row[0]
        trigger.processors = row[1]
        print('fuck [' + str(trigger.filters) + ']')
        return trigger