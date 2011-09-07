#What is this craxy thing?

This is the current, production version of "Eventgrinder"-- which runs some calendar aggregator sites, like dctechevents.com

#Whatgrinder?

It's an editorial system for calendars, which includes an iCal aggregator, user submissions, and an editorial queue.

#Why does this code suck so much?

Lot's of reasons! Here's a few:

* I didn't concieve of it as open source, and it never occured to me that someone else might see the code.
* Testing? LOL
* There are a lot of half-implemented ideas in the code. 
* It only runs on AppEngine
* It's written in at least two frameworks (Django and Tipfy), with a little bit of hacky WSGI middleware thrown in for reasons I forget.

# What is most broken?

The aggregator really needs to be made smarter-- particularly, it should handle events that disappear from iCal feeds (it should assume they are cancelled, postponed, or at least flag them as having possible issues)

If other people are going to hack on this and use it, a real theming system probably needs to appear. Also, the current "theme" is pretty ugly.

The current system of navigating between weeks is just dumb.

Recurring events were once supported, but it never worked very well, so I took it out. They should probably come back (done right).
