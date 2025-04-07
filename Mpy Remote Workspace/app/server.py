from microdot import Microdot, Response
from microdot.session import Session
from app.mm_wlan import connect_to_network
from app.routes import register_routes
from config.parametres import ssid, password, token_secret

app = Microdot()
Response.default_content_type = 'text/html'
connect_to_network(ssid, password)
Session(app, secret_key=token_secret)

register_routes(app)

