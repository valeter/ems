#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import logging


class TriggerProcessorService:
    def __init__(self, queue_service, triggers_topic_config):
        self.queue_service = queue_service
        self.topic = triggers_topic_config['name']
        self.consumer_group_id = triggers_topic_config['consumer_group_id']
        self.processors = {}

    def add_processor(self, trigger_type, processor):
        if self.processors[trigger_type] == None:
            self.processors[trigger_type] = []
        self.processors[trigger_type].append(processor)

    def process_triggers(self):
        self.queue_service.process_messages(self.topic, self.process_trigger)

    def process_trigger(self, trigger_json):
        trigger = json.loads(trigger_json)
        for processor in self.processors[trigger['type']]:
            processor(trigger)


class TriggerToMessageProcessor:
    def __init__(self, message_service, user_service, channel, template):
        self.message_service = message_service
        self.channel = channel
        self.template = template

    def get_message(self, trigger):
        message = {}
        message['channel'] = self.channel
        message['address'] = user_service.get_address(trigger['userId'], self.channel)
        message['userId'] = trigger['userId']
        message['template'] = self.template
        message['tags'] = trigger['tags']
        message['model'] = {}
        message['model']['trigger-data'] = trigger['data']

    def process(self, trigger):
        message = get_message(message)
        self.message_service.add_message(json.dumps(message))