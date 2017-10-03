#!/usr/bin/python
# -*- coding: utf-8 -*-

from kafka import KafkaProducer
from kafka import KafkaConsumer


class QueueService:
    def __init__(self, kafka_config):
        self.kafka_config = kafka_config
        self.consumers = {}

    def init(self):
        self.producer = KafkaProducer(
            bootstrap_servers='{0}:{1}'.format(self.kafka_config['host'], self.kafka_config['port'])
        )

    def send(self, topic, message):
        return self.producer.send(topic=topic, value=message)

    def subscribe(self, topic, consumer_group_id):
        if self.consumers[topic] != None:
            return
        self.consumers[topic] = KafkaConsumer(
            topic,
            bootstrap_servers='{0}:{1}'.format(self.kafka_config['host'], self.kafka_config['port']),
            client_id=self.kafka_config['client_id'],
            group_id=consumer_group_id,
        )

    def process_messages(self, topic, callback):
        for msg in self.consumers[topic]:
            callback(msg)