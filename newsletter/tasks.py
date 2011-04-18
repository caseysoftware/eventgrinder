from google.appengine.ext import db
from google.appengine.api import mail

from newsletter.models import Edition


import subscriptions.models
import eventsite.models

from datetime import datetime

import logging, os, hashlib
from yaro import Yaro

from google.appengine.ext.db import Query
from google.appengine.api.labs.taskqueue import Queue, Task, TaskAlreadyExistsError, TombstonedTaskError
MailQueueExpander=Queue(name='mail-queue-expander')
SendNewsletter=Queue(name='send-newsletter')


class MailBatch(db.Model):
    pass

class PendingEmail(db.Model):
    edition=db.ReferenceProperty(Edition, required=True)
    subscription=db.ReferenceProperty(subscriptions.models.Subscription, required=True)
    sent_on=db.DateTimeProperty()

@Yaro
def send_newsletter(request):
    message=db.get(request.form['pending_email'])
    if message.sent_on: return
    edition=message.edition
    to=message.subscription.parent().email
    sender="%s <%s@%s.appspotmail.com>"%(edition.site.name,edition.site.slug, os.environ['APPLICATION_ID'])
    subject=edition.subject
    body=edition.body_txt
    html=edition.body_html
    def _tx():
            message.sent_on=datetime.now()
            message.put()

            
    batch=db.run_in_transaction_custom_retries(10,_tx)
    mail.send_mail(sender,to,subject ,body, html=html)
            


@Yaro
def mail_queue_expander(request):
    BATCH_SIZE=5
    edition=db.get(request.form['edition'])
    if not edition: pass
    page=int(request.form.get('page',0))
    subscriber_q=Query(subscriptions.models.Subscription, keys_only=True).filter('site =', edition.site).filter('active =', True)
    if request.form.has_key('cursor'):
        subscriber_q=subscriber_q.with_cursor(request.form['cursor'])
    subscribers=subscriber_q.fetch(BATCH_SIZE)
    if not subscribers:
        edition.status='complete'
        edition.put()
        return
    task=Task(params={'edition':edition.key(),
                      'cursor': subscriber_q.cursor(), 
                      'page':page+1},
                      name="%s-%s-%s-%s" %(edition.site.slug, edition.issue_num,edition.publish_after.strftime("%Y%j%H%M-%S"), page+1)
                      
                      )
    try:
        MailQueueExpander.add(task)
    except (TaskAlreadyExistsError, TombstonedTaskError):
        raise
    for sub in subscribers:
        def _tx():

                pending_email=PendingEmail(subscription=sub, edition=edition)
                db.put(pending_email)  
                SendNewsletter.add(Task(params={'pending_email':pending_email.key()}), transactional=True)
        db.run_in_transaction_custom_retries(10,_tx)

    