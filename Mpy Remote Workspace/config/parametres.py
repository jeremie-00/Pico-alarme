def load_dotenv(filepath='.env'):
    env_vars = {}
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    return env_vars



env_vars = load_dotenv()
#paramétrage notification    
""" param_pushsafer = {
    'cle_api_pushsafer' : env_vars.get("KEY_PUSHSAFER"),
               'device' : env_vars.get("DEVICE_PUSHSAFER"),
               
                'icon'  : {'cloche'  : "1",
                           'warning' : "5",
                           'cle'     : "12",
                           'buzzer'  : "56"},
                
                'sound' : {'buzzer': "61",
                     'alarme-armed': "51",
                 'alarme-disarmed' : "52",
                     'door-closed' : "54",
                     'door-closed' : "55",
                       'bip-court' : "61",
                        'bip-long' : "62"},
                
            'vibration' : ["0","1","2","3"],  
            'time2live' : '0',
             'priority' : ["-2","-1","0","1","2"],       
} """
param_pushsafer = {
    'cle_api_pushsafer' : env_vars.get("KEY_PUSHSAFER"),
               'device' : env_vars.get("DEVICE_PUSHSAFER"),
               
                'icon'  : '5',
                
                'sound' : '8',
                
            'vibration' : '2',  
            'time2live' : '0',
             'priority' : '0',       
}
#parametres wifi station ou AP
ssid=env_vars.get("SSID")
password=env_vars.get("PASSWORD")
# key token
token_secret=env_vars.get("TOKEN_SECRET")
# port
port=int(env_vars.get("PORT"))
#mode WIFI
#mode_wifi = 'AP_IF'
mode_wifi = {'STATION' : 'STA_IF',
'ACCESS_POINT': 'AP_IF'}





