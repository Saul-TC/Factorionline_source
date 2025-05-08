import getpass
import os
import re
import git
import time
import shutil
import subprocess

from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from rich.progress import Progress, BarColumn, TextColumn, TransferSpeedColumn, TimeElapsedColumn

from .logger import Log
from .utilities import Notification

name = 'FileManager' # For log
repo_url = 'https://github.com/Saul-TC/factorionline.git'
factorionline_path = os.path.join(os.getenv('APPDATA'), 'Factorio\\factorionline')
factorio_saves_path = os.path.join(os.getenv('APPDATA'), r'Factorio\saves\Factorionline')


class ChangeHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.active = False
        self.changed = False
    def on_deleted (self, event):
        if self.active:
            self.changed = True
    def activate (self):
        self.active = True
    def deactivate (self):
        self.active = False

    

class FileManager:
    def __init__(self, logger:Log):
        self.logger = logger
        self.repo = None
        self.origin = None
        self.activated = False
        self.running = False
        self.path_exists = False
        self.path_disapears = False
        self.observer = Observer()
        self.change_handler = ChangeHandler()

    
    def removeDir (self, dir:str) -> bool:
        try:
            shutil.rmtree(dir)
            return True
        except FileNotFoundError:
            return False
    

    def add_safe_directory(self, path):
        try:
            subprocess.run(
                ["git", "config", "--global", "--add", "safe.directory", path],
                check=True
            )
            print(f"Directorio {path} agregado como seguro.")
        except subprocess.CalledProcessError as e:
            print(f"Error agregando directorio seguro: {e}")


    def ensure_safe_directory(self, path):
        try:
            result = subprocess.run(
                ["git", "config", "--global", "--get-all", "safe.directory"],
                capture_output=True, text=True, check=True
            )
            safe_dirs = result.stdout.splitlines()

            if path not in safe_dirs:
                self.add_safe_directory(path)
            else:
                print(f"Directorio {path} ya estaba marcado como seguro.")
        except subprocess.CalledProcessError:
            self.add_safe_directory(path)

        
    def copyDir (self, src:str, dst:str) -> bool:
        try:
            shutil.copytree(src, dst)
            return True
        except FileExistsError:
            return False
        

    def updateDir (self, src:str, dst:str) -> bool:
        self.removeDir(dst)
        if self.copyDir(src, dst):
            return True
        return False
        


    def activate (self):
        self.logger.info('FileManager activated.', name, style='green')
        if self.activated:
            self.logger.info('FileManager already active.')
            return True
        # Crear el objeto repo antes de mover la carpeta con las partidas 'Factorionline'
        try:
            self.repo = git.Repo(factorionline_path)
            self.origin = self.repo.remotes.origin
            if self.pullRepo():
                self.change_handler.activate()
            else:
                return False
        except Exception as e:
            self.logger.critical(f'{e}', name)
            return False
        
        # Mover la carpeta para que se puedan acceder desde factorio
        try:
            self.observer = Observer()
            self.updateDir(factorionline_path+'\\Factorionline', factorio_saves_path)
            self.observer.schedule(self.change_handler, path=factorio_saves_path, recursive=True)
            self.observer.start()
            self.activated = True
        except Exception as e:
            self.logger.critical(f'Unexpected exception: {e}', name)
            return False

        self.activated = True
        return True
        

    def run (self):
        # Observar cuando se sobreescriba alguna partida compartida, entonces hacer push
        self.running = True
        self.path_exists = os.path.exists(factorionline_path)
        self.logger.info('Running FileManager', name, style='bold green')
        last_path_check = self.path_exists
        while self.running:
            self.path_exists = os.path.exists(factorionline_path)
            if not self.path_exists:
                self.running = False
                if last_path_check:
                    self.path_disapears = True
                break
            last_path_check = self.path_exists
            if self.change_handler.changed:
                self.logger.info('Save file changed.')
                if self.activated:
                    self.updateDir(factorio_saves_path, factorionline_path+'\\Factorionline')
                    if not self.pushRepo():
                        title = 'Error al guardar partida!'
                        message = 'Se produjo un error al intentar guardar partida.'
                        Notification(title=title, message=message, config={'sound': 'IM'})
                self.change_handler.changed = False
            time.sleep(1)
        self.logger.info('FileManager stoped.', name)


    def deactivate (self):
        self.change_handler.deactivate()
        self.removeDir(factorio_saves_path)
        if self.observer:
            self.observer.stop()
            self.observer = None
        self.activated = False
        self.logger.info('FileManager deactivated.', name)
    

    def stop (self):
        self.deactivate()
        self.running = False


    def git_progress(self, command, progress_regex, action, repo_path=None, notification:bool=False, text_fields:list=None):
        if notification:
            noti = Notification(
                text_fields[0],
                text_fields[1],
                config={
                    'is_interactable': True,
                    'audio': 'default',
                    'duration': 'long',
                    'widgets': [{
                        'type': 'progress_bar',
                        'label': text_fields[2]
                    }]
                }
            )
            noti.show()


        
        progress = Progress(
            TextColumn(action, style='bold cyan'),
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            TransferSpeedColumn(),
            TimeElapsedColumn(),
            redirect_stdout=True
        )
        with progress:
            task = progress.add_task(command, total=100)
            if repo_path:
                process = subprocess.Popen(
                    ["git", "-C", repo_path] + command.split()[1:],
                    stderr=subprocess.PIPE,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                process = subprocess.Popen(
                    command.split(),
                    stderr=subprocess.PIPE,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            for line in process.stderr:
                if 'Receiving objects' in line or 'Writing objects' in line:
                    match = progress_regex.search(line)
                    if match:
                        percent = int(match.group(1))
                        progress.update(task, completed=percent)
                        if notification:
                            noti.update_progress_bar(percent/100)
            process.wait()
    
        if process.returncode == 0:
            if notification:
                noti.update_progress_bar(float(percent/100))
                time.sleep(1)
                noti.remove()
            return True
        else:
            return False



    def cloneRepo(self):
        self.logger.info('Cloning repo.', name, style='cyan')
        clone_regex = re.compile(r'Receiving objects:\s+(\d+)%')
        text_fields = [
            'Estamos descargando las partidas compartidas, espere un momento.',
            'Iniciando factorionline.',
            'Clonando repositorio.'
        ]
        if self.git_progress(f'git clone --progress {repo_url} {factorionline_path}', clone_regex, 'Cloning repo', notification=True, text_fields=text_fields):
            self.add_safe_directory(factorionline_path)
            self.logger.info('Repo cloned.', name)
            return True
        self.logger.info('Repo could not clone.', name)
        return False

    def pullRepo(self):
        self.logger.info('Pulling repo.', name, style='cyan')
        pull_regex = re.compile(r'Receiving objects:\s+(\d+)%')
        if self.git_progress("git pull --progress", pull_regex, 'Pulling repo', repo_path=factorionline_path):
            self.logger.info('Repo pulled.', name)
            return True
        self.logger.info('Repo could not pull.', name)
        return False


    def pushRepo(self):
        self.logger.info('Pushing repo', name, style='cyan')
        push_regex = re.compile(r'Writing objects:\s+(\d+)%')
        self.repo.git.add(all=True)
        self.repo.index.commit(datetime.now().isoformat())
        text_fields = [
            'Estamos subiendo tu progreso al repositorio.',
            'Guardando progreso.',
            'Subiendo datos.'
        ]
        if self.git_progress('git push --progress', push_regex, 'Pushing repo', repo_path=factorionline_path, notification=True, text_fields=text_fields):
            self.logger.info('Repo pushed.', name, style='bold cyan')
            return True
        self.logger.info('Repo could not push.', name, style='bold cyan')
        return False