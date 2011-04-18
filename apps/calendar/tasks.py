from google.appengine.ext import db
from google.appengine.api.labs import taskqueue
import vobject

import logging
from resolver import resolve

from tipfy import RequestHandler, Response, url_for

from models import SourceProcessTicket, iCalSnippet, SourcedEvent



class ProcessSourceCalendarHandler(RequestHandler):
	def post(self):
		driver=resolve(self.request.form['driver'])
		# handle unknown drivers
		driver(**self.request.form)
		
		return Response()
		



class StartFetchSourceCalendar(RequestHandler):
	def post(self):
		logging.info("StartFetchSourceCalendar running")
		calendar_key_str=self.request.form.get('calendar')
		if calendar_key_str:
			calendar_key=db.Key(calendar_key_str)
			ticket=SourceProcessTicket(source_calendar=calendar_key)
			ticket.put()
			# enqueue ProcessSourceCalendarHandler with calendar, and resolver statement
			# pointing to driver-appropriate "process" function 
			calendar=db.get(calendar_key)
			task_params={
				'driver':"apps.calendar.drivers.%s:process" % calendar.driver,
				'ticket':ticket.key(),
				'calendar':calendar.key()
			}
			taskqueue.add(url=url_for("calendar/tasks/process_source_calendar"), params=task_params)
		
		return Response()
		
class ProcessiCalSnippets(RequestHandler):
	def extract_times(self,vevent):
		return (vevent.dtstart.value, vevent.dtend.value)

	def post(self):
		ticket_key=db.Key(self.request.form['ticket'])
		snippets_q=iCalSnippet.all().filter('ticket =', ticket_key)
		
		if self.request.form.get('cursor'):
			snippets_q.with_cursor(self.request.form.get('cursor'))

		next_snippet=snippets_q.get()
		if next_snippet:
			parsedCal = vobject.readOne(next_snippet.ical)
			vevent=parsedCal.vevent
			#todo-- run this in transaction
			#todo-- name the task
			task_params={
			'ticket':self.request.form['ticket'],
			'cursor':snippets_q.cursor()
			}
			taskqueue.add(url=url_for("calendar/tasks/process_ical_snippets"), params=task_params)
			dtstart, dtend = self.extract_times(vevent)
			title=vevent.summary or "Untitled Event"
			start=vevent.dtstart.value
			logging.warning(start)
			#event=SourcedEvent()
		else:
			pass
			#enque cleanup
		
		
		# if no cursor, get the first snippet
		# transform into a Event object with a resonable key
		# re-enqueue with cursor
		return Response()