import os
import sys

import pyvert
import portend
import cherrypy
from pyvert import logger


from pyvert.webserve import WebInterface


def initialize(options):
    # HTTPS stuff stolen from sickbeard
    enable_https = options['enable_https']
    https_cert = options['https_cert']
    https_key = options['https_key']

    if enable_https:
        # If either the HTTPS certificate or key do not exist,
        # try to make self-signed ones.

        logger.warn('PyVert WebStart :: Disabled HTTPS because of' +
                    ' missing certificate and key.')
        enable_https = False

    options_dict = {
        'server.socket_port': options['http_port'],
        'server.socket_host': options['http_host'],
        'environment': options['http_environment'],
        'server.thread_pool': 10,
        'tools.encode.on': True,
        'tools.encode.encoding': 'utf-8',
        'tools.decode.on': True
    }

    if enable_https:
        options_dict['server.ssl_certificate'] = https_cert
        options_dict['server.ssl_private_key'] = https_key
        protocol = 'https'
    else:
        protocol = 'http'

    if not options['http_root'] or options['http_root'] == '/':
        pyvert.HTTP_ROOT = options['http_root'] = '/'
    else:
        pyvert.HTTP_ROOT = options['http_root'] = '/' + options['http_root'].strip('/') + '/'

    cherrypy.config.update(options_dict)

    conf = {
        '/': {
            'tools.staticdir.root': os.path.join(pyvert.PROG_DIR, 'data'),
            'tools.gzip.on': True,
            'tools.gzip.mime_types': ['text/html', 'text/plain', 'text/css',
                                      'text/javascript', 'application/json',
                                      'application/javascript'],
            'tools.auth_basic.realm': 'PyVert web server',
        },
        '/images': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'interfaces/default/images',
            'tools.caching.on': True,
            'tools.caching.force': True,
            'tools.caching.delay': 0,
            'tools.expires.on': True,
            'tools.expires.secs': 60 * 60 * 24 * 30,  # 30 days
        },
        '/css': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': "interfaces/default/css",
            'tools.caching.on': False,
            'tools.caching.force': False,
            'tools.caching.delay': 0,
        },
        '/js': {
             'tools.staticdir.on': True,
             'tools.staticdir.dir': "interfaces/default/js",
             'tools.caching.on': False,
             'tools.caching.force': False,
             'tools.caching.delay': 0,
        }
    }

    # Prevent time-outs
    cherrypy.engine.timeout_monitor.unsubscribe()
    cherrypy.tree.mount(WebInterface(), options['http_root'], config=conf)

    try:
        logger.info('PyVert WebStart :: Starting PyVert web server ' +
                    'on {0}://{1}:{2}{3}'.format(protocol,
                                                 options['http_host'],
                                                 options['http_port'],
                                                 options['http_root']))
        # cherrypy.process.servers.check_port(str(options['http_host']),
        #                                     options['http_port'])
        portend.Checker().assert_free(str(options['http_host']), options['http_port'])
        cherrypy.server.start()
    except IOError:
        sys.stderr.write('Failed to start on port: {0}. Is something else running?\n'.format(options['http_port']))
        sys.exit(1)

    cherrypy.server.wait()
