from google.appengine.ext import db
from google.appengine.api.labs import taskqueue
from google.appengine.api import urlfetch, memcache

from tipfy import url_for, Response


import logging
import chardet

from apps.calendar.models import iCalSnippet

#future improvements: abstract out memcache, database, and taskqueue


def split_ical(ical):
	first_vevent_start=ical.find('BEGIN:VEVENT')
	cal_meta=ical[0:first_vevent_start]

	def next_vevent(start):
		end=ical.find('END:VEVENT',start)
		if end > -1:
			end=end+10
			cal=cal_meta+ical[start:end]+"\nEND:VCALENDAR"
			return (cal, end)
		else:
			return(None, None)
	vevent, index=next_vevent(first_vevent_start)   
	while vevent:
		yield vevent
		vevent, index=next_vevent(index)

def process(**kwargs):
	if not kwargs.get('phase'):
		calendar=db.get(kwargs['calendar'])[0]
		logging.warning('started fetching %s'% calendar.title )
		result=urlfetch.fetch(calendar.source_uri, allow_truncated=True, deadline=5)
		detection=chardet.detect(result.content)
		
		memcache.add("%s-source" % kwargs['ticket'][0], result.content.decode(detection['encoding']))
		logging.warning("cached ical source with key %s" % "%s-source" % kwargs['ticket'][0])
		
		
		task_params={
				'driver':"apps.calendar.drivers.%s:process" % calendar.driver,
				'ticket':kwargs['ticket'][0],
				'calendar':kwargs['calendar'][0],
				'phase':'split'
			}
		taskqueue.add(url=url_for("calendar/tasks/process_source_calendar"), params=task_params)
		
	elif kwargs['phase'][0] == 'split':
		ticket=db.Key(kwargs['ticket'][0])
		calendar=db.Key(kwargs['calendar'][0])
		ical_source=memcache.get("%s-source" % kwargs['ticket'][0])
		snippets=[]
		for snippet in split_ical(ical_source):
			snippets.append(iCalSnippet(ticket=ticket, ical=snippet, calendar=calendar, parent=ticket))
		
		def save_and_process_snippets():
			db.put(snippets)
			task_params={
				'ticket':kwargs['ticket'][0],
				'calendar':kwargs['calendar'][0],
			}
			taskqueue.add(url=url_for("calendar/tasks/process_ical_snippets"), params=task_params, transactional=True)
		db.run_in_transaction(save_and_process_snippets)
		
			
			
	