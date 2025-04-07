from machine import Pin
import utime
import uasyncio as asyncio
from time import sleep
import gc

from utils.file_management import save_file, read_file
from config.parametres import param_pushsafer
from utils.pushsafer import Client
from utils.set_time import set_rtc_time

class Checkpoints:
    instances_chkpts = []
    MAX_HISTORIQUE = 50

    def __init__(self, **kwargs):
        self.tasks = []
        for key, value in kwargs.items():
            if key == 'gpio':
                setattr(self, 'gpio',(int(value)))
                self.update_pin()
            if key == 'id':
                setattr(self, key,(int(id(self))))
            else:
                setattr(self, key, value)

#-----SUPPRESSION DES TASKS-----#
    def delete_tasks(self):
        if self.tasks:
            for task in self.tasks:
                task.cancel()
            self.tasks.clear()
    
    @classmethod
    def nettoyage(cls, variable):
        del variable
        gc.collect()

    @classmethod
    def reset_class(cls):
        cls.instances_chkpts.clear()
        cls.nettoyage(cls.instances_chkpts)

    @classmethod
    def instance_exists(cls, data):
        return any(instance.name == data.name or instance.gpio == data.gpio for instance in cls.instances_chkpts)
########## MAJ FICHIER INSTANCE ##################
    @classmethod
    def convertion_instance_dico(cls):
        # Convertit les instances de la classe Checkpoints en dictionnaires
        serialized_checkpoints = []
        for chkpt in cls.instances_chkpts:
            chkpt_dict = {key: value for key, value in chkpt.__dict__.items() if key != 'pin' and key != 'tasks'}
            chkpt_dict['state'] = chkpt.pin.value() 
            serialized_checkpoints.append(chkpt_dict)
        return serialized_checkpoints

    @classmethod
    def update_fichier(cls):
        return save_file('checkpoints.json', cls.convertion_instance_dico())
########## MAJ FICHIER HISTORIQUE ##################
    @classmethod
    def add_event(cls, icon, message):
        historique = read_file("historique.json")
        historique.append([icon ,f'le {set_rtc_time().get("date")} à {set_rtc_time().get("heure")}' ,f'{message}'])
        if len(historique) > cls.MAX_HISTORIQUE:
            historique = historique[-cls.MAX_HISTORIQUE:]
        save_file("historique.json", historique)
        cls.nettoyage(historique)
        
######## CREATION DES INSTANCE ###############
    @classmethod
    def create_instance(cls, data):
        cls.reset_class()
        for chkpt_data in data:
            instance = cls(**chkpt_data)
            if not cls.instance_exists(instance):
                cls.instances_chkpts.append(instance)
        cls.update_fichier()
        cls.nettoyage(instance)

    @classmethod
    def add_instance(cls, data):
        instance = cls(**data)
        cls.instances_chkpts.append(instance)
        response = cls.update_fichier()
        cls.add_event({"color": "blue", "iconeName":"add"}, f"{instance.name} a été ajouter")
        cls.nettoyage(instance)
        return response

    @classmethod
    def get_instances(cls):
        return cls.instances_chkpts
###### STATE PICO W #####
    @classmethod
    def check_si_ouvert(cls):
        return any(cls.est_ouvert(objet) for objet in cls.instances_chkpts)

    def est_ouvert(self):
        return bool(self.pin.value())

    @classmethod
    def gpio_libre(cls):
        gpio_disponibles = list(range(10, 21))
        for instance in cls.instances_chkpts:       
            if instance.gpio:           
                gpio_disponibles.remove(int(instance.gpio))
        return gpio_disponibles
###### UPDATE INSTANCE #####
    def update_pin(self):
        if hasattr(self, 'gpio'):
            self.pin = Pin(self.gpio, Pin.IN, Pin.PULL_UP)
            
    @classmethod
    def update_instance(cls, id , data):
        for instance in cls.instances_chkpts:     
            if instance.id == id:
                cls.nettoyage(id)
                initial_state = {key: getattr(instance, key) for key in data.keys() if hasattr(instance, key)}
                #print("Avant la mise à jour :", instance.__dict__)
                for key, value in data.items():
                    if hasattr(instance, key):
                        if key == 'potl' and value == False:
                            instance.delete_tasks()
                        setattr(instance, key, value)
                        cls.nettoyage(key)
                        cls.nettoyage(value)
                        cls.nettoyage(data)
                        #print("Mise à jour de la cle", key, "avec la valeur", value, "pour l'instance", instance.name, "avec gpio", instance.gpio)
                    else:
                        #print("L'attribut", key, "n'existe pas dans l'instance", instance.name, "avec gpio", instance.gpio)
                        return False
                instance.update_pin()
               
                final_state = {key: getattr(instance, key) for key in data.keys() if hasattr(instance, key)}
                cls.nettoyage(data)
                modifications = {key: {'avant': initial_state[key], 'après': final_state[key]} for key in initial_state if initial_state[key] != final_state[key]}
                cls.nettoyage(initial_state)
                cls.nettoyage(final_state)                
                message_retour = f'{instance.name} a été modifié. <br>' 
                for cle, valeur in modifications.items():
                    if cle == 'potl':
                        message_retour += f'{cle} : {"Activer" if valeur["avant"] else "Désactiver"} --> {"Activer" if valeur["après"] else "Désactiver"} <br>'
                    else:    
                        message_retour += f'{cle} : {valeur["avant"]} --> {valeur["après"]} <br>'

                cls.add_event({"color": "blue", "iconeName":"up"}, message_retour)
                cls.update_fichier()
                cls.nettoyage(cle)
                cls.nettoyage(valeur)
                cls.nettoyage(message_retour)
                return True
        return False

    @classmethod
    def update_date(cls, name, new_date):
        for instance in cls.instances_chkpts:
            if instance.name == name:
                instance.alarme = new_date
        cls.update_fichier()

    @classmethod
    def convert_time_to_decimal(cls, time_str):
        hours, minutes = map(int, time_str.split(":"))
        return hours + minutes / 60.0

    @classmethod
    def is_within_alarm_period(cls,current_hour, start_hour, end_hour):
        current_hour = cls.convert_time_to_decimal(current_hour)
        start_hour = cls.convert_time_to_decimal(start_hour)
        end_hour = cls.convert_time_to_decimal(end_hour)
        if start_hour < end_hour:
            # Plage horaire sans chevauchement de minuit (ex. 8h-18h)
            return start_hour <= current_hour < end_hour
        else:
            # Plage horaire avec chevauchement de minuit (ex. 22h-6h)
            return current_hour >= start_hour or current_hour < end_hour


    @classmethod
    def update_surveillance(cls, value):
        data = read_file("options.json")
        result = set_rtc_time()
        heure = result.get('heure')
        start = data.get('start')
        end = data.get('end')
        manual = data.get('autoModeBypass')
        cls.nettoyage(data)
        cls.nettoyage(result)
        within_period = cls.is_within_alarm_period(heure, start, end)
        if cls.check_si_ouvert() and value:
            chkpt_open = [instance.name for instance in cls.instances_chkpts if instance.est_ouvert()]
            if chkpt_open:
                open_list = ', '.join(chkpt_open)
                verb = "sont" if len(chkpt_open) > 1 else "est"
                plural = "s" if len(chkpt_open) > 1 else ""
                message = f"Mise en service impossible : {open_list} {verb} ouverte{plural}"
                return False, False, message
        if not cls.instances_chkpts:
            return False, False, 'Aucune porte programmée'

        for instance in cls.instances_chkpts:
            instance.surveillance = value
            if not value:
                instance.alarme = None

        message = "Surveillance activée" if value else "Surveillance désactivée"
        cls.add_event({"color": "green" if value else "red", "iconeName": "mes" if value else "mhs"}, message)
        cls.update_fichier()
        return True, value, message


    @classmethod
    def auto_surveillance(cls):
        data = read_file("options.json")
        if data.get('auto'):
            result = set_rtc_time()
            heure = result.get('heure') 
            start = data.get('start')
            end = data.get('end')
            manual = data.get('autoModeBypass')
            cls.nettoyage(data)
            #print('hours', heure)
            #print('------------------------')
            within_period = cls.is_within_alarm_period(heure, start, end)
            #print('reponse is_within_alarm_period', within_period)
            #print('-----------------------')

            for instance in cls.get_instances():
                if within_period and not instance.surveillance:
                    cls.update_surveillance(True)
                    
                    #print('############################')
                   # print("Alarme en service", instance.surveillance)
                    #print('############################')
                elif not within_period and instance.surveillance and not manual:
                    cls.update_surveillance(False)
                   
                    #print('############################')
                    #print("Alarme hors service", instance.surveillance)
                    #print('############################')

    @classmethod
    def get_data_chkpts(cls, id):
        liste_objets = read_file('checkpoints.json')
        chkpts = [objet for objet in liste_objets if objet['id'] == id]
        cls.nettoyage(liste_objets)
        return chkpts[0]

    @classmethod
    def delete_instance_fichier(cls, id):
        liste_objets = read_file('checkpoints.json')
        updated_list = [objet for objet in liste_objets if objet['id'] != id]
        if len(updated_list) < len(liste_objets):
            for instance in cls.instances_chkpts:
                if instance.id == id:
                    instance.delete_tasks()
                    cls.instances_chkpts.remove(instance)
                    message = f"{instance.name} a été supprimer"
            cls.add_event({"color": "red", "iconeName":"del"}, message)
            cls.update_fichier()
            cls.nettoyage(liste_objets)
            return True
        else:
            cls.nettoyage(liste_objets)
            return False

#-----GESTION NOTIFICATION-----# 
    @staticmethod
    def force_gc_collect():
        gc.collect()
        print("Mémoire libre après collecte:", gc.mem_free())

    async def envoi_notif(self):
        client = Client(param_pushsafer.get('cle_api_pushsafer'))
        message = f'Effraction à {self.alarme.get('heure')} le {self.alarme.get('date')}' if self.surveillance else f'Declanchement du buzzer à {self.alarme.get('heure')} le {self.alarme.get('date')}' 
        self.force_gc_collect()
        try:
            # print("avant notif", title, message)
            await client.send_message(message, title=self.name, device=param_pushsafer.get('device'), icon=param_pushsafer.get('icon'), sound=param_pushsafer.get('sound'), vibration=param_pushsafer.get('vibration'), priority=param_pushsafer.get('priority'))   
            cls.nettoyage(message)
            cls.nettoyage(param_pushsafer)
        except Exception as e:
            print(f"Erreur lors de l'envoi de la notification: {e}")
        return True

#-----CHRONOMETRE ET BUZZER-----#
    async def generer_son_discontinu(self,duree_on, duree_off, nombre_repetitions):
        buzz = Pin(3,Pin.OUT)
        self.add_event({"color": "red", "iconeName":"buzz"},f"POTL activer sur {self.name} porte ouverte")
        while self.pin.value() == 1:
            for _ in range(nombre_repetitions):
                print("buz", _ , self.name)                   
                buzz.on()
                await asyncio.sleep(duree_on)
                buzz.off()
                await asyncio.sleep(duree_off)            
            await asyncio.sleep(10)
         
    async def chronometre(self):
        #print(' CHRONO DEBUT \n',self.name +'\n')
        start_time = utime.ticks_ms()
        #print('start time', start_time)
        run = True
        while run: 
            if self.pin.value() == 0:
                run = False

            elapsed_time = utime.ticks_diff(utime.ticks_ms(), start_time)

            seconds = elapsed_time // 1000
            minutes, seconds = divmod(seconds, 60)
            hours, minutes = divmod(minutes, 60)
            milliseconds = elapsed_time % 1000

            temps_ecouler = "{:02d}:{:02d}:{:02d}.{:03d}".format(hours, minutes, seconds, milliseconds) 
            tempo = self.chrono.split(":")
            temps_max = "{:02d}:{:02d}:{:02d}.{:03d}".format(int(tempo[0]), int(tempo[1]), int(tempo[2]), 0)
            #print('elapsed_time', elapsed_time)
            await asyncio.sleep(1)           
            if temps_ecouler >= temps_max:
                run = False  
                #print('fini ', temps_ecouler >= temps_max)
                task_buzz = asyncio.create_task(self.generer_son_discontinu(0.1,0.5,5))
                self.tasks.append(task_buzz) 

#-----fin CHRONOMETRE ET BUZZER--------#  


