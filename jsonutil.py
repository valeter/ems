#!/usr/bin/python
# -*- coding: utf-8 -*-

import json


class Payload(object):
  def __init__(self, j):
    self.__dict__ = json.loads(j)

def parse_json(j):
  return Payload(j)

def to_json(obj):
  return json.dumps(obj, default=lambda o: o.__dict__, sort_keys=True)