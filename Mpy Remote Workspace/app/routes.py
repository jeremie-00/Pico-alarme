from machine import Pin
import gc

import urandom
import json
import hashlib
import binascii

from microdot import Response, redirect, send_file, Request
from microdot.session import with_session

from utils.file_management import save_file, read_file
from utils.checkpoints import Checkpoints as chkpts
from utils.validate_checkpoint_data import validate_checkpoint_data
from utils.set_time import set_rtc_time
from utils.led_pico import toggle_onboard_led

def register_routes(app):

    def nettoyage(variable):
        del variable
        gc.collect()

    def Surveillance():
        instances_chkpts = chkpts.get_instances()
        if not instances_chkpts:
            nettoyage(instances_chkpts)
            return False
        for chkpt in instances_chkpts:
            if chkpt.surveillance:
                nettoyage(instances_chkpts)
                return True
            nettoyage(instances_chkpts)
            return False

    def load_users():
        try:
            with open('/config/users.json', 'r') as file:
                users = json.load(file)
        except Exception as e:
            print(f"Erreur lors du chargement des utilisateurs : {e}")
            users = None
        finally:
            nettoyage(file)
        return users

    def get_users():
        return load_users()

    def hash_password(password):
        hash = hashlib.sha256(password.encode()).digest()
        return binascii.hexlify(hash).decode('utf-8')

    def log_session(fu, session):
        print(f"Session Data: {fu}", session)

    def require_login(handler):
        @with_session
        async def wrapper(request: Request, session, *args, **kwargs):
            if session.get('username') and session.get('id'):
                #log_session("wrap",session)
                request.g.username = session.get('username')
                request.g.id = session.get('id')
                return await handler(request, *args, **kwargs)
            else:
                return redirect('/login')
        return wrapper      

    def authenticate_login(request):
        form_data = request.form
        username = form_data.get('username')
        password = form_data.get('password')
        users = get_users()
        if users is None:
            return False
    
        hashed_password = hash_password(password)
        if username in users and hashed_password == users.get(username):
            nettoyage(users)
            return True

        nettoyage(users)
        return False
        #ip, port= request.client_addr 


    def login_file():
        try:
            with open('static/login.html', 'r') as f:
                return f.read()                            
        except OSError:
            print('login introuvable')
            return '<html><body>login introuvable</body></html>'

    @app.post('/login')
    @app.get('/login')
    @with_session
    async def login_page(request: Request, session):
        if request.method == 'GET':
            message_html = ''
            if 'error' in request.args:
                message_html = "Identification incorrecte !"
            html = login_file()
            html = html.format(message=message_html)
            response = Response(body=html)
            response.headers['Content-Type'] = 'text/html'
            nettoyage(html)
            return response
        elif request.method == 'POST':
            if authenticate_login(request):
                session_id = urandom.getrandbits(32)
                session = request.g._session
                session['username'] = request.form.get('username')
                session["id"] = session_id
                session.save()
                return redirect('/')
            else:
                return redirect(f'/login?error=1')

    @app.get('/logout')
    @require_login
    @with_session
    async def logout(request, session):
        session = request.g._session
        session.delete()
        nettoyage(session)
        return redirect('/login')

    @app.get('/shutdown')
    @require_login
    async def shutdown(request):
        chkpts.reset_class()
        request.app.shutdown()
        return 'The server is shutting down...'

    @app.get('/')
    @require_login
    async def index(request):
        try:
            return send_file('index.html')
        except OSError as e:
            if e.errno == 104:
                print("Connexion réinitialisée par le client")
                return Response(status_code=500, text="Erreur de connexion")
            else:
                raise

    @app.errorhandler(Exception)
    def handle_exception(request, exception):
        print(f"Erreur: {exception}")
        return Response(status_code=500, body="Une erreur s'est produite")

    @app.route('/static/<path:path>')
    async def static(request, path):
        if '..' in path:
            return 'Not found', 404
        try:
            toggle_onboard_led()
            return send_file('static/' + path, max_age=86400) #, max_age=86400
        except OSError as e:
            print(f"Error serving file {path}: {e}")
            return 'Internal Server Error', 500

# RECUPERATION DE TOUTE LES DATAS
    @app.get('/getAllData')
    @require_login
    async def getAllData(request):
        response_data = {
            "dataChkpts": chkpts.convertion_instance_dico(),
            "gpioDispo": chkpts.gpio_libre(),
            "surveillance": Surveillance(),
            "options": read_file('options.json'),
            'memory': f" Mémoire libre: {gc.mem_free()}"
        }
        response = Response(json.dumps(response_data), headers={'Content-Type': 'application/json'})
        nettoyage(response_data)
        gc.collect()
        return response


# HISTORIQUE
# lecture du fichier historique pour envoi de data
    @app.get('/getHistorique')
    @require_login
    async def getHistorique(request):
        async def stream_historique():
            try:
                with open('../static/json-files/historique.json', 'r') as file:
                    while True:
                        chunk = file.read(1024)  # Lire par morceaux de 1024 octets
                        if not chunk:
                            break
                        yield chunk
            except Exception as e:
                yield json.dumps({"error": str(e)})
            finally:
                gc.collect()
        return Response(stream_historique(), headers={'Content-Type': 'application/json'})
# recuperation du dernier historique
    @app.get('/getLastHistorique')
    @require_login
    async def getLastHistorique(request):
        data = read_file('/historique.json')
        lastHistorique = data[-1]
        nettoyage(data)
        return {'lastHistorique': lastHistorique }

# GPIO
    @app.get('/getGpio')
    @require_login
    async def getGpio(request):
        return {'gpioDispo': chkpts.gpio_libre() }

# OPTIONS
    @app.put('/putTitle')
    @require_login
    async def putTitle(request):
        options = read_file('options.json')
        old_name = options['title']
        options['title'] = request.json['title'].get('title')
        success = save_file('options.json', options)
        if success:
            chkpts.add_event({"color": "blue", "iconeName":"up"},f"Modification du titre<br>{old_name} --> {options['title']}") 
        nettoyage(options)
        nettoyage(old_name)
        return {'success': success}

    @app.put('/putSpeak')
    @require_login
    async def putSpeak(request):
        options = read_file('options.json')
        options['speak'] = request.json['speak']
        success = save_file('options.json', options)
        options_speak = options['speak']
        nettoyage(options)
        if options_speak:
            chkpts.add_event({"color": "green", "iconeName":"son"},f"Activation de la synthèse vocale") 
        else:
            chkpts.add_event({"color": "red", "iconeName":"mute"},f"Désactivation de la synthèse vocale") 
        return {'success': success, 'rep': options_speak}

# CHECKPOINTS
    @app.get('/getDataChkpts')
    @require_login
    async def getData(request):
        serialized_checkpoints = chkpts.convertion_instance_dico()
        resp = json.dumps(serialized_checkpoints)
        nettoyage(serialized_checkpoints)
        return resp

    @app.get('/chkpts/<int:id>')
    @require_login
    async def getChkptsForUpdate(request, id):
        data = chkpts.get_data_chkpts(id)
        success = True if data else False
        return {'success': success, 'data': data, 'gpioDispo': chkpts.gpio_libre() }

    @app.post('/chkpts')
    @require_login
    async def addChkpts(request):
        data = request.json.get('data', {})
        is_valid, message = validate_checkpoint_data(data)
        if not is_valid:
            nettoyage(data)
            return {'success': False, 'error': message}
        success = chkpts.add_instance(data)
        nettoyage(data)
        return {'success': success, 'message': message}

    @app.patch('/chkpts/<int:id>')
    @require_login
    async def updateChkpts(request, id):
        data = request.json.get('data', {})
        is_valid, message = validate_checkpoint_data(data)
        if not is_valid:
            nettoyage(data)
            return {'success': False, 'error': message}
        success = chkpts.update_instance(id , data)
        nettoyage(data)
        return {'success': success, 'message': message}

    @app.delete('/chkpts/<int:id>')
    @require_login
    async def deleteChkpts(request, id):
        success = chkpts.delete_instance_fichier(id)
        return {'success': success }

# SURVEILLANCE ET AUTOSURVEILLANCE
    @app.get('/getSurveillance')
    @require_login
    async def getSurveillance(request):
        data = read_file("options.json")
        auto_mode_bypass = data.get('autoModeBypass')
        auto = data.get('auto')
        nettoyage(data)
        return {'success': Surveillance(), 'autoModeBypass' : auto_mode_bypass, 'auto':auto}

    @app.patch('/patchSurveillance')
    @require_login
    async def patchSurveillance(request):
        data = read_file("options.json")
        result = set_rtc_time()
        heure = result.get('heure') 
        within_period = chkpts.is_within_alarm_period(heure, data.get('start'), data.get('end'))
        data['autoModeBypass'] = True if data.get('auto') and request.json['surveillance'] and not within_period else False
        success = save_file('options.json', data)
        auto_mode_bypass = True if data.get('auto') and request.json['surveillance'] and not within_period else False
        auto = data.get('auto')
        nettoyage(data)
        nettoyage(within_period)
        success, value, message = chkpts.update_surveillance(request.json['surveillance'])
        return {'success': success, 'value': value , 'message' : message, 'autoModeBypass' : auto_mode_bypass, 'auto':auto}

    @app.patch('/patchAutoSurveillance')
    @require_login
    async def patchAutoSurveillance(request):
        data_request = request.json.get('data', {})
        data = read_file("options.json")
        data['auto'] = data_request.get('auto')
        data['start'] = data_request.get('start')
        data['end'] = data_request.get('end')
        if not data_request.get('auto'): 
            data['autoModeBypass'] = False
        result = set_rtc_time()
        heure = result.get('heure')
        start = data_request.get('start')
        end = data_request.get('end')
        is_surveillance_active = chkpts.is_within_alarm_period(heure, start, end)
        nettoyage(result)
        nettoyage(heure)
        nettoyage(start)
        nettoyage(end)
        success = save_file('options.json', data)
        if data_request.get('auto'):
            chkpts.add_event({"color": "blue", "iconeName":"time"},f"Plage horaire activer de {data_request.get('start')} à {data_request.get('end')}")
        else:
            chkpts.add_event({"color": "blue", "iconeName":"finger"},f"Plage horaire désactiver")
        nettoyage(data)
        nettoyage(data_request)
        return {'success': success , 'isSurveillance' : is_surveillance_active}

