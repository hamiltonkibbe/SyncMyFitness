#!/usr/bin/env python
#
#   syncmyfitness.py
#
#   A script for syncing your workout data from other sites with MapMyFitness
#   Run it from a cron job daily or whatever. I ended up doing this all the
#   time because I use Nike+ to track all my running but my company health
#   plan uses MapMyFitness to decide whether or not to give me a discount...
#
#   Anything worth doing twice is worth automating...
#
#   Copyright (C) 2014 Hamilton Kibbe <ham@hamiltonkib.be>
#
#   Everyone is permitted to copy and distribute verbatim or modified
#   copies of this license document, and changing it is allowed as long
#   as the name is changed.
#
#           DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
#
#   0. You just DO WHAT THE FUCK YOU WANT TO.


import cookielib
import urllib
import urllib2

# Either fill these out here, or pass them as command line arguments
EMAIL = ''
PASSWORD = ''


def sync_data(email=EMAIL, password=PASSWORD, service='nikeplus'):
    ''' Sync workout data with MapMyFitness. Email and Password are your
    login credentials. Returns True on success, False on failure
    '''
    
    auth_url = 'https://www.mapmyfitness.com/auth/login/'
    import_url = 'http://www.mapmyfitness.com/workout/import/'
    sync_url = _get_sync_url(service)
    
    
    # Set up urllib opener to handle cookies and https
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPSHandler(),urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-agent', 'Nike+ sync script... contact me at %s' % EMAIL)] # be polite
    urllib2.install_opener(opener)
    
    # Fill out the login form data
    data = urllib.urlencode({'csrfmiddlewaretoken':'', 'email': email, 'password': password})

    # Hit the login page, then post the loginform
    resp = urllib2.urlopen(urllib2.Request(auth_url))
    resp = urllib2.urlopen(urllib2.Request(auth_url, data))
    
    # press the magic "Sync" button. The referer header might not be necessary
    resp = urllib2.urlopen(urllib2.Request(sync_url, headers={'Referer':import_url}))
    
    # return sync status
    return ('sync was sucessfully completed' in resp.read())


def _get_sync_url(service):
    ''' Return the url of the sync endpoint for the given service
    '''
    service = service.lower()
    base = 'http://www.mapmyfitness.com/workout/import/%s/sync'
    url = None
    # Services list
    if service in ['nike+', 'nikeplus' ,'nike_plus', 'nike']:
        url = base % 'nikeplus'
    elif service in ['fitbit',]:
        url = base % 'fitbit'
    elif service in ['garmin']:
        url = base % 'garmin'
    elif service in ['jawbone']:
        url = base % 'jawbone'
    else:
        raise ValueError('%s is not a currently supported service.' % service)
    
    return url    


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Sync workout data with MapMyFitness')
    parser.add_argument('-e', '--email', help='The email associated with your MapMyFitness account', default=EMAIL)
    parser.add_argument('-p', '--password', help='The password associated with your MapMyFitness account', default=PASSWORD)
    parser.add_argument('-s', '--service', help='The service to sync (nikeplus, fitbit, etc....)',default='nikeplus')
    args = parser.parse_args()

    success = sync_data(args.email, args.password, args.service)
    
    if success:
        print('Sync successful')
    else:
        print('Sync failed.')
        
