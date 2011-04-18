from tipfy import Rule

def get_rules(app):
    rules = [
        Rule('/links/add', endpoint="links/add", handler='apps.links.handlers.AddLinkHandler'),
        Rule('/links/review', endpoint="links/review", handler='apps.links.handlers.ReviewLinksHandler'),
		Rule('/links/change', endpoint="links/change-status", handler='apps.links.handlers.ChangeLinkStatusHandler'),
		
    ]

    return rules