# -*- coding: utf-8 -*-
"""
    main
    ~~~~

    Run Tipfy apps.

    :copyright: 2009 by tipfy.org.
    :license: BSD, see LICENSE for more details.
"""
import os
import sys

if 'lib' not in sys.path:
    # Add /lib as primary libraries directory, with fallback to /distlib
    # and optionally to distlib loaded using zipimport.
    sys.path[0:0] = ['lib', 'distlib', 'distlib.zip', 'shared']
    

import config
import tipfy

# Is this the development server?
debug = os.environ.get('SERVER_SOFTWARE', '').startswith('Dev')

# Instantiate the application.
app = tipfy.make_wsgi_app(config=config.config, debug=debug)
from tipfy.ext.jinja2 import get_jinja2_instance
env=get_jinja2_instance()
env.globals['app_version'] = os.environ['CURRENT_VERSION_ID'] or 'dev'

def main():

	app.run()


if __name__ == '__main__':
    main()
