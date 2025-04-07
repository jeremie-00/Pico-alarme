import uasyncio as asyncio
import errno
#import urequests

from utils.file_management import read_file
from utils.checkpoints import Checkpoints as chkpts
from app.server import app
from app.mm_wlan import is_connected
from utils.set_time import set_rtc_time

from utils.led_pico import toggle_onboard_led#, blink_onboard_led
import gc
from config.parametres import port

def stop_server():
    chkpts.reset_class()
    app.shutdown()
    print("Serveur arrêté.")

async def start_server():
    if not is_connected():
        print("Pas de connexion réseau.")
        return
    print("RTC mis à jour après démarrage du serveur.")
    set_rtc_time()
    try:
        print("Tentative de démarrage du serveur...")
        await app.start_server(port=port, debug=True)
    except OSError as exc:
        if exc.errno == errno.EADDRINUSE: #98
            print("Port déjà utilisé. Arrêt du serveur.")
            stop_server()
            await asyncio.sleep(1)
            await app.start_server(port=port, debug=True)
        else:
            raise

def log_memory_usage(message):
    gc.collect()
    gc.threshold()
    #print(f"{message} - Mémoire libre: {gc.mem_free()}")
    #print(f"{message} - Mémoire allouer: {gc.mem_alloc()}")

async def monitor_checkpoints():
    while True:
        log_memory_usage("Avant surveillance des checkpoints")
        chkpts.auto_surveillance() 
        toggle_onboard_led()
        for checkpoint in chkpts.get_instances():    
            if checkpoint.surveillance:
                interval = 1 
                if checkpoint.est_ouvert() and checkpoint.alarme is None:
                    chkpts.update_date(checkpoint.name, set_rtc_time())
                    chkpts.force_gc_collect()
                    asyncio.create_task(checkpoint.envoi_notif())
                    checkpoint.add_event({"color": "red", "iconeName":"alert"},f"Alarme {checkpoint.name} ouverte")
                    # print("Mémoire libre :", gc.mem_free())      
            else:
                interval = 2
                #name = checkpoint.name
                if checkpoint.est_ouvert() and checkpoint.potl and not checkpoint.tasks:
                    task_chrono = asyncio.create_task(checkpoint.chronometre())
                    checkpoint.tasks.append(task_chrono)
                elif not checkpoint.est_ouvert() and checkpoint.potl:
                    checkpoint.delete_tasks()  
        await asyncio.sleep(interval)
        

async def main():
    data_checkpoints = read_file('checkpoints.json')
    chkpts.create_instance(data_checkpoints)
    del data_checkpoints
    gc.collect()
    server_task = asyncio.create_task(start_server())
    monitor_task = asyncio.create_task(monitor_checkpoints())
    await asyncio.gather(server_task, monitor_task)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("KeyboardInterrupt: Stopping the server...")
        stop_server()
    except Exception as e:
        print("An error occurred during main loop:", e)
