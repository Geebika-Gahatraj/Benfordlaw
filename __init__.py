from pyramid.config import Configurator

config = Configurator()
config.include('pyramid_jinja2')
config.add_route('home', '/')
config.add_route('benford', '/benford')
config.scan()
app = config.make_wsgi_app()
from waitress import serve
serve(app, host='0.0.0.0', port=8080)