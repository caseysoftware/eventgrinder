from tipfy import Rule

def get_rules(app):
    rules = [
        Rule('/calendars/', endpoint="calendar/index", handler='apps.calendar.handlers.IndexHandler'),
        Rule('/calendars/add', endpoint="calendar/add", handler='apps.calendar.handlers.AddCalendarHandler'),
    	Rule('/calendars/<calendar_slug>/edit', endpoint="calendar/edit", handler="apps.calendar.handlers.EditCalendarHandler"),
    	Rule('/calendars/initiate_fetch', endpoint="calendar/fetch", handler="apps.calendar.handlers.FetchCalendarHandler"),
    	Rule('/tasks/start_fetch_source_calendar',
    			endpoint="calendar/tasks/start_fetch_source",
    			handler="apps.calendar.tasks.StartFetchSourceCalendar"),
    	Rule('/tasks/process_source_calendar',
    			endpoint="calendar/tasks/process_source_calendar",
    			handler="apps.calendar.tasks.ProcessSourceCalendarHandler"),
    			
    	Rule('/tasks/process_ical_snippets',
    		endpoint="calendar/tasks/process_ical_snippets",
    		handler="apps.calendar.tasks.ProcessiCalSnippets"),
    ]

    return rules