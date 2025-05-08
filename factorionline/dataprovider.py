import os
import socket
import time
import asyncio
import firebase_admin
from datetime import datetime
from firebase_admin import credentials, firestore_async


from .logger import Log
from .fatorioerror import FactorioError, ErrorFixed


name = 'DataProvier' # For log
cred = {}
cred = credentials.Certificate(cred)
app = firebase_admin.initialize_app(cred, {
            'databaseURL': 'factorionline-61308.firebaseapp.com'
        })
db = firestore_async.client()


class DataProvider:
    def __init__(self, logger:Log):
        self.logger = logger
        self.user = os.getlogin()
        self.running = False
        self.check = False
        self.online = False
        self.heartbeat = False
        self.available = False
        self.lost_connection = False


    async def checkForUsersOnline (self):
        data = await db.collection('sesiones').document('last_report').get()
        if self.online and data:
            data = data.to_dict()
            last_report = data.get('datetime', '')
            user = data.get('user', '')
            try:
                difference = datetime.now() - datetime.fromisoformat(last_report)
                if data and user != self.user and difference.total_seconds() <= 60*5:
                    return True
                else:
                    return False
            except:
                return True
        else:
            return True
        

    def run (self):
        self.logger.info('Running DataProvider.', name, style='bold green')
        self.running = True
        asyncio.run(self.mainloop())


    async def mainloop (self):
        sec = 0
        self.online = await self.testConnection()
        self.last_check = self.online
        while self.running:
            time.sleep(1)
            sec += 1
            if sec >= 60 or self.check:
                if self.check:
                    self.check = False
                self.online = await self.testConnection()
                if self.online:
                    if self.heartbeat:
                        await self.updateHeartbeat()
                    self.available = not await self.checkForUsersOnline()
                elif self.last_check:
                    self.lost_connection = True
                    self.available = False
                self.last_check = self.online
                sec = 0
        self.logger.info('DataProvider stoped.', name)


    async def updateHeartbeat (self):
        """Actualiza en el servidor que el cliente sigue en linea. Retorna `False` si falla."""
        ref = db.collection('sesiones').document('last_report')
        await ref.set({'datetime': datetime.now().isoformat(), 'user': self.user})
        self.logger.debug(f'Heartbeat: {datetime.now().isoformat()}', name)
        if await self.checkForUsersOnline():
            return False
        else:
            return True

    
    def connect (self) -> bool:
        """Permite enviar al servidor una actualización constante del estado de conxión, para evitar que otro usuario se conecte a la vez."""
        if self.heartbeat:
            self.logger.info('DataProvider already connected.')
            return 0
        self.check = True
        time.sleep(4)
        if self.online:
            if self.available:
                self.heartbeat = True
                self.logger.debug('DataProvider connected.', name, style='bold')
                return 0
            else:
                return 1
        else:
            return 2
    

    def disconnect (self) -> None:
        self.heartbeat = False
        self.logger.info('DataProvider dissconected.', name)

    
    def stop (self):
        self.disconnect()
        self.running = False
        

    async def testConnection (self) -> bool:
        """Retorna el estado del server, devuelve False si el server no está
        activo o si no hay respuesta, devuelve True en caso contrario"""
        if not self.testInternetConnection():
            self.logger.debug(f'Connection tested: {False}', name, style='red')
            return False
        data = await db.collection('data').document('server_state').get()
        if data:
            is_online = data.to_dict().get('online', False)
        self.logger.debug(f'Connection tested: {is_online}', name)
        if data and is_online:
            self.online = True
            return True 
        else:
            self.online = False
            return False
    
    def testInternetConnection (self):
        try:
            socket.setdefaulttimeout(3)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(('8.8.8.8', 53))
            return True
        except socket.error:
            return False