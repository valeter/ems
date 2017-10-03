#!/usr/bin/python
# -*- coding: utf-8 -*-

class MessageService:
    def __init__(self, validation_service, queue_service, messages_topic_config):
        self.validation_service = validation_service
        self.queue_service = queue_service
        self.topic = messages_topic_config['topic']

    def add_message(self, messsage_json):
        self.validation_service.validate_json("message", messsage_json)
        self.queue_service.send(self.topic, messsage_json)