from mapreduce import operation as op
import logging
import appengine_config
from events.models import Event

def process(entity):
    yield op.db.Put(entity)
    return
