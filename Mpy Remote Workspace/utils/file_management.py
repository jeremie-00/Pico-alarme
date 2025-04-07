import json
import gc

from utils.set_time import set_rtc_time

def options_origine():
    #date,heure = set_rtc_time()
    default ={ 
        "title" : "Title par default",
        "speak" : False,
        "start" : "22:00",
        "end"   : "07:00",
        "auto" : False,
        "autoModeBypass" : False,
        }   
    return default

def param_origine():
    #date,heure = set_rtc_time()
    default =[{ 
        "name"         : "nom par default1",
        "gpio"         : 14,  
        "alarme"       : None,
        "surveillance" : False,
        "id"           : None,
        "potl"         : False,
        "chrono"       :"00:00:00",
        "tasks"        :[],
        },{ 
        "name"         : "nom par default2",
        "gpio"         : 15,  
        "alarme"       : None,
        "surveillance" : False,
        "id"           : None,
        "potl"         : False,
        "chrono"       :"00:00:00",
        "tasks"        :[],
        },{ 
        "name"         : "nom par default3",
        "gpio"         : 16,  
        "alarme"       : None,
        "surveillance" : False,
        "id"           : None,
        "potl"         : False,
        "chrono"       :"00:00:00",
        "tasks"        :[],
        },{ 
        "name"         : "nom par default4",
        "gpio"         : 17,  
        "alarme"       : None,
        "surveillance" : False,
        "id"           : None,
        "potl"         : False,
        "chrono"       :"00:00:00",
        "tasks"        :[],
        }]         
    return default

def histo_origine():
    return []

def save_file(fichier, data):
    try:
        with open('/static/json-files/' + fichier, "w") as f:
            json.dump(data, f, separators=(' , \n', ' : '))
            #print(f"-------------------")
            #print(f"{fichier} ENREGISTRER") 
            #print(f"-------------------")
            del data
            del f
            gc.collect()
            return True
    except Exception as e:
        #print(f"Une erreur s'est produite lors de l'enregistrement du fichier {fichier} : {e}") 
        return False
         
def read_file(fichier):
    if fichier == "options.json":
        default = options_origine()
    elif fichier == "historique.json":
        default = histo_origine()
    else:
        default = param_origine()   
    data = None
    try:
        with open('/static/json-files/' + fichier, 'r') as f:
            try:
                data = json.load(f)                            
            except ValueError as e:
                #print(f'probleme dans le fichier {fichier} creation par default')
                data = default
                save_file(fichier, data) 
    except OSError:
        #print(f'{fichier} introuvable creation du fichier par default')
        data = default
        save_file(fichier, data)
    if not data:
        data = default
        save_file(fichier, data)
    del default
    gc.collect()
    return data 

