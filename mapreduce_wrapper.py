import os

from google.appengine.ext.webapp import util

def main():
    os.environ['DJANGO_SETTINGS_MODULE']='techevents_settings'
    from mapreduce.main import APP
    util.run_wsgi_app(APP)



if __name__ == '__main__':
  main()
