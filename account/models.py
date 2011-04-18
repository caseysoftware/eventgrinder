from google.appengine.ext import db
from aetycoon import DerivedProperty

from eventsite.models import Eventsite

# import code for encoding urls and generating md5 hashes
import urllib, hashlib, os


class Profile(db.Model):
    nickname=db.StringProperty(required=False, indexed=False)
    link=db.LinkProperty(required=False, indexed=False)
    email=db.EmailProperty(required=False)
    slug=db.StringProperty(required=False)
    site=db.ReferenceProperty(Eventsite)
    user=db.UserProperty()
    confirmed_at=db.DateTimeProperty(required=False)
    # Verification stuff
    verified_at=db.DateTimeProperty(required=False)
    # Permission stuff
    userlevel=db.IntegerProperty(required=True, default=0)
    subscribes=db.BooleanProperty(required=False, default=0)
    
    def verify_email(self,email):
        key_string= email+ str(datetime.now())
        md5=hashlib.md5()
        md5.update(key_string)
        verification=PendingVerification(parent=self, proposed_email=email, code=md5.hexdigest())
    
    @property
    def is_editor(self):
        return (self.userlevel > 9)

    
    
    @property
    def profile_details(self):
        return{'nickname': self.nickname,
                'email': self.email or self.user.email,
                'subscribes':self.subscribes or False}
    
    @property
    def gravatar(self):
	    size=15
	    gravatar = "http://www.gravatar.com/avatar.php?"
	    gravatar += urllib.urlencode({'gravatar_id':hashlib.md5(self.email).hexdigest(),  'size':str(size), 'd':'monsterid'})
	    return gravatar

	 
def slugify(value):
        """
        Normalizes string, converts to lowercase, removes non-alpha characters,
        and converts spaces to hyphens.
        Borrowed from Django, while trying to decouple my models from Django itself
        """
        import unicodedata
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
        value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
        return unicode(re.sub('[-\s]+', '-', value))