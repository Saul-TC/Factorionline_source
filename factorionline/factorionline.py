import subprocess
import sys
import threading
import pathlib
import psutil
import time
import os



from .logger import Log
from .filemanager import FileManager, factorionline_path
from .register_hkey_aumid import register_hkey
from .dataprovider import DataProvider
from .utilities import Notification
from .fatorioerror import FactorioError, ErrorFixed
name = 'Factorionline' # For log

class Factorionline:
    factorio_process_name = 'factorio.exe'
    def __init__(self, logger:'Log'):
        self.logger = logger
        self.running = False
        self.process_active = False
        self.notify_online = True
        self.notified_offline = False
        self.on_entry = False
        self.do_stop = False
        self.on_exit = False
        self.do_disconnect = False
        self.connecting = False
        self.filemanager = FileManager(self.logger)
        self.dataprovider = DataProvider(self.logger)

    def asktask (self):
        try:
            subprocess.run(
                ["schtasks", "/Query", "/TN", 'Factorionline'],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False
        

    def firstExecution (self):
        if not self.asktask():
            subprocess.run([
                "schtasks",
                "/Create",
                "/SC", "ONLOGON",
                "/TN", 'Factorionline',
                "/TR", sys.executable,
                "/RL", "HIGHEST"
            ], check=True)
        try:
            os.makedirs(factorionline_path)
            if not self.filemanager.cloneRepo():
                return False
        except Exception as e:
            self.logger.critical(f'Unexpected exception: {e}', name)
            return False
        
        try:
            # Registra el nombre de factorionline
            register_hkey('Saul.Factorionline','Factorionline', pathlib.Path(factorionline_path + '\\factorionline.ico'))
            self.logger.debug('AUMID registered', name)
        except:
            self.logger.error('AUMID couldn\'t be created.', name)
            return False
        return True


    def setUp (self):
        if self.firstExecution():
            self.logger.debug('Everything configured.', name)
        else:
            self.logger.error('SetUp fails.', name)
            return False
        return True


    def run (self):
        # Inicia el mainloop de la conexión a la base de datos
        threading.Thread(target=self.dataprovider.run).start()
        threading.Thread(target=self.filemanager.run).start()
        self.running = True
        threading.Thread(target=self.processListening).start()
        self.mainLoop()


    def mainLoop (self):
        while self.running:
            try:
                if self.on_entry:
                    self.onEntry()
                if self.on_exit:
                    self.onExit()
                if self.do_stop:
                    self.stop()
                if self.do_disconnect:
                    self.disconnect()
                if self.connecting:
                    if self.dataprovider.available:
                        if self.notify_online and not self.process_active:
                            self.notifyUser('online_avaible')
                        if self.process_active:
                            self.on_entry = True
                        self.connecting = False
                if self.dataprovider.lost_connection:
                    self.logger.debug('Connection Lost', name)
                    self.dataprovider.lost_connection = False
                    self.notified_offline = True
                    raise FactorioError(FactorioError.LostConnectionError)
                if self.filemanager.path_disapears:
                    self.logger.warning('Root path disapears.')
                    if self.setUp():
                        self.filemanager.path_disapears = False
                        threading.Thread(target=self.filemanager.run).start()
            except FactorioError as fe:
                error_id = fe.args[0].get('id')
                self.logger.warning(error_id, name)
                match (fe.args[0]):
                    case FactorioError.ConnectionError:
                        self.connecting = True
                        if not self.notified_offline:
                            self.notifyUser('offline_mode')
                            self.notified_offline = True
                    case FactorioError.LostConnectionError:
                        self.connecting = True
                        if self.process_active:
                            self.notifyUser('offline')
                    case FactorioError.SomeoneAlreadyPlaying:
                        self.connecting = True
                        self.notifyUser('someone_already_playing')
                    case _:
                        self.logger.error(error_id, name)
            except ErrorFixed:
                if self.process_active:
                    self.on_entry = True
        time.sleep(1)


    
    def onEntry (self):
        if not os.path.exists(factorionline_path):
            self.logger.warning('Root directory isn\'t exists.', name)
            if not self.setUp():
                self.stop()
                return False
        self.on_entry = False
        self.logger.debug('On entry.', name)
        # Aqui va la logica al entrar al juego
        if self.dataprovider.online:
            response = self.dataprovider.connect()
            if response == 0:
                if not self.filemanager.activate():
                    raise FactorioError(FactorioError.FileManagerFail)
                self.notifyUser('online')
                return True
            elif response == 1:
                raise FactorioError(FactorioError.SomeoneAlreadyPlaying)
            else:
                raise FactorioError(FactorioError.ConnectionError, self.dataprovider)
        else:
            raise FactorioError(FactorioError.ConnectionError, self.dataprovider)
        return False


    def disconnect (self):
        self.dataprovider.disconnect()
        self.filemanager.deactivate()


    def onExit (self):
        self.on_exit = False
        if not self.connecting:
            self.disconnect()
        self.logger.debug('Exit.', name)


    def processListening (self) -> None:
        def checkProcess () -> bool:
            """Busca si factorio está en ejecución"""
            for proceso in psutil.process_iter(['name']):
                if proceso.info['name'] == self.factorio_process_name:
                    return True
            return False
        

        self.logger.info('Running Factorionline.', name, style='bold green')
        self.process_active = False
        # Mainloop
        while self.running:
            if checkProcess():
                if not self.process_active:
                    self.process_active = True
                    self.on_entry = True
                    self.notified_offline = False
            else:
                if self.process_active:
                    self.process_active = False
                    self.on_exit = True
            time.sleep(1)
        self.logger.info('Factorionline stoped.', name)


    def stop (self) -> None:
        self.running = False
        self.dataprovider.stop()
        self.filemanager.stop()

    
    def notifyUser (self, id:str) -> None:
        """Notifica al usuario de alguna situación.
        ## Params
        ### id (str) Options:
        - 'online' = El usuario se acaba de conectar con factorionline.
        - 'offline_mode' = El usuario entró a factorio en modo offline.
        - 'offline' = El usuario perdió conexión con el server.
        - 'online_avaible' = El usuario ya puede jugar en partidas compartidas.
        - 'downloading' = Se esta descargando el repositorio."""
        self.logger.debug(f'Notification throwed. ID: {id}', name)
        match (id):
            case 'online':
                title = 'Conexión establecida'
                message = 'Se estableció conexión con factorionline! Ahora estás al día con tus partidas. Haz cick aquí para entrar en modo offline.'
                Notification(message, title, config={
                    'is_interactable':True,
                    'action': self.handleAction,
                    'audio': 'default',
                    'widgets': [{
                        'type': 'button',
                        'label': 'Entrar en modo offline.',
                        'response': 'offline'
                    }]
                    }).show()
            case 'offline':
                title = 'Conexión perdida!'
                message = 'Se perdió la conexión con factorionline, ahora corres el peligro de perder tu progreso. \U0001F628'
                Notification(message, title, config={'audio': 'IM'}).show()
            case 'offline_mode':
                title = 'No se pudo establecer conexión con factorionline.'
                message = 'Entrando en modo offline, no podrás jugar en partidas compartidas. Te avisaremos en caso de reconexión.'
                Notification(message, title, config={'audio': 'IM'}).show()
            case 'someone_already_playing':
                title = 'Factorionline no disponible. Alguien mas ya está jugando ahora mismo.'
                message = 'Entrando en modo offline, no podrás jugar en partidas compartidas.'
                Notification(message, title, config={
                    'is_interactable':True,
                    'action': self.handleAction,
                    'audio': 'IM',
                    'widgets': [{
                        'type': 'button',
                        'label': 'No me notifiques! Ya no quiero \U0001F624',
                        'response': 'dont_notify_online'
                    }]
                    }).show()
            case 'online_avaible':
                title = 'Online disponible!'
                message = 'Ahora ya puedes jugar partidas online.'
                Notification(message, title, config={
                    'is_interactable':True,
                    'action': self.handleAction,
                    'widgets': [{
                        'type': 'button',
                        'label': 'Entrar al juego.',
                        'response': 'open_factorio'
                    }]
                }).show()
            case 'saved':
                title = 'Partida guardada.'
                message = 'Tu progreso se guardo exitosamente.'
                Notification(message, title).show()
    
    
    def handleAction (self, response:str):
        self.logger.debug(f'Notification actioned. Response: {response}', name)
        match (response):
            case 'offline':
                self.onExit()
            case 'dont_notify_online':
                self.notify_online = False
            case 'open_factorio':
                self.openFactorio()
            case _:
                self.logger.error(f'Invalid notification response. Default case statement: {response}', name)
    

    def openFactorio (self) -> None:
        subprocess.run([r'C:\GOG Games\Factorio\bin\x64\factorio.exe'])


    def killFactorioProcess (self) -> bool:
        killed = True
        for proceso in psutil.process_iter(['name']):
            if proceso.info['name'] == self.factorio_process_name:
                try:
                    proceso.terminate() 
                    killed = True
                except psutil.NoSuchProcess:
                    pass
                except psutil.AccessDenied:
                    return False
                except Exception:
                    return False
        return killed
# End class Factorionline    

# def throwError(error_name:str, config=0) -> None:
#     """
#     config values
#     0: ok
#     1: ok cancel
#     2: abort retry ignore
#     3: yes no cancel
#     4: yes no
#     5: retry cancel
#     6: cancel try-again continue
#     """
#     error = FactorioError.errors.get(error_name, None)
#     error_message = error.get('message', 'default_error_message')
#     if not error:
#         raise Exception(f'Error id does not exists. ({error_name})')
#     return Dialog('error', error_message, title='Oops!', config=config).show()