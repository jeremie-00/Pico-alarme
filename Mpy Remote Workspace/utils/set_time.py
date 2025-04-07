import machine
import gc
import requests

def get_datetime_online():
    try:
        response = requests.get('http://worldtimeapi.org/api/timezone/Europe/Paris')        
        data = response.json() 
        year = int(data['datetime'][0:4])
        month = int(data['datetime'][5:7])
        date = int(data['datetime'][8:10])
        hour = int(data['datetime'][11:13])
        minute = int(data['datetime'][14:16])
        second = int(data['datetime'][17:19])
        return year, month, date, 0, hour, minute, second, 0
    except Exception as e:
        print("Erreur lors de la récupération de l'heure en ligne:", e)
        return None
            
def set_rtc_time():
    #print('RTC FUNCTION')
    rtc = machine.RTC()
    current_time = rtc.datetime()
    if current_time[0] < 2024:    
        new_datetime = get_datetime_online()
        if new_datetime is not None:
            rtc.datetime(new_datetime) 
            print("Horloge RTC réglée avec succès à partir de l'heure en ligne.")
            current_time = rtc.datetime()      
            date = "{:02d}-{:02d}-{:04d}".format(current_time[2], current_time[1], current_time[0])
            heure = "{:02d}:{:02d}:{:02d}".format(current_time[4], current_time[5], current_time[6])
            return date, heure
    
    current_time = rtc.datetime()      
    date = "{:02d}-{:02d}-{:04d}".format(current_time[2], current_time[1], current_time[0])
    heure = "{:02d}:{:02d}".format(current_time[4], current_time[5])
    gc.collect()
    return {'date' : date, 'heure' : heure}