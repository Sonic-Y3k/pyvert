import os
import cherrypy
from cherrypy.lib.static import serve_file, serve_download
from cherrypy._cperror import NotFound
from mako.lookup import TemplateLookup
from mako import exceptions
import pyvert


def serve_template(templatename, **kwargs):
    interface_dir = os.path.join(str(pyvert.PROG_DIR), 'data/interfaces')
    template_dir = os.path.join(str(interface_dir), pyvert.CONFIG.INTERFACE)

    _hplookup = TemplateLookup(directories=[template_dir],
                               default_filters=['unicode', 'h'])

    server_name = 'PyVert'

    try:
        template = _hplookup.get_template(templatename)
        return template.render(http_root=pyvert.HTTP_ROOT,
                               server_name=server_name,  **kwargs)
    except:
        return exceptions.html_error_template().render()


class WebInterface(object):
    def __init__(self):
        self.interface_dir = os.path.join(str(pyvert.PROG_DIR), 'data/')

    @cherrypy.expose
    def index(self, **kwargs):
        raise cherrypy.HTTPRedirect(pyvert.HTTP_ROOT + "home")

    @cherrypy.expose
    def home(self, **kwargs):

        return serve_template(templatename="home.html", title="Home")
