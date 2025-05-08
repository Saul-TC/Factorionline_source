import time
import windows_toasts as wt

class Notification:
    appname = 'Factorionline'
    durations = {
        'short': wt.ToastDuration.Short,
        'long': wt.ToastDuration.Long,
        'default': wt.ToastDuration.Default
    }
    def __init__ (self, message:str, title:str, config:dict=None):
        self.message = message
        self.title = title
        self.config = config if config else {
            'is_interactable': False,
            'widgets': [],
            'action': None,
            'duration': wt.ToastDuration.Default,
            'dissmis': None,
            'audio': 'default',
            'audio_looping': False
        }
        self.toast = wt.Toast(self.appname)
        self.toast.duration = self.durations[self.config.get('duration', 'default')]
        self.toast.text_fields = [self.title, self.message]
        self.on_action = self.config.get('action', None)
        self.on_dissmised = self.config.get('dissmis', None)

        widgets = self.config.get('widgets', None)
        self.toaster = wt.InteractableWindowsToaster(self.appname, r'Saul.Factorionline')
        if self.config.get('is_interactable', False):
            if widgets:
                self.make_widgets(widgets)

        match (self.config.get('audio', 'default')):
            case 'default':
                audio_source = wt.AudioSource.Default
            case 'IM':
                audio_source = wt.AudioSource.IM
            

        self.toast.audio = wt.ToastAudio(audio_source, looping=self.config.get('audio_looping', False))
        self.toast.on_activated = self.action
        self.toast.on_dismissed = self.dissmis


    # Add widwets to the notification body
    def make_widgets (self, widgets):
        for w in widgets:
            match (w.get('type')):
                case 'button':
                    widget = wt.ToastButton(w.get('label'), w.get('response'))
                    self.toast.AddAction(widget)
                case 'progress_bar':
                    widget = wt.ToastProgressBar(status=w.get('label'))
                    self.toast.progress_bar = widget
                case _:
                    raise TypeError('Invalid widget type.')

    
    def update_progress_bar (self, progress:float):
        self.toast.progress_bar.progress = progress
        if progress >= 1:
            self.toast.progress_bar.status = 'Completado!'
        self.toaster.update_toast(self.toast)
    

    def remove (self):
        self.toaster.remove_toast(self.toast)


    # Throw notification
    def show (self):
        self.toaster.show_toast(self.toast)


    # Enters always when notification is actioned
    def action (self, activatedEventArgs: wt.ToastActivatedEventArgs):
        if self.on_action:
            self.on_action(activatedEventArgs.arguments)
        else:
            return activatedEventArgs.arguments


    # Enters always when notification is dissmised
    def dissmis (self, dismissdEventArgs: wt.ToastDismissedEventArgs):
        self.toaster.remove_toast(self.toast)



class Dialog:
    """
    Icons:
    error
    warning
    question
    info
    nothing
    Config buttons values:
    code | returns
    0: ok
    1: ok cancel
    2: abort retry ignore
    3: yes no cancel
    4: yes no
    5: retry cancel
    6: cancel try-again continue
    """
    def __init__(self, title:str, message:str, icon:str, type:int, delay:int=0):
        self.title = title
        self.message = message
        self.icon = icon
        self.type = type
        self.delay = delay
    
    def show (self) -> str:
        time.sleep(self.delay)
        match (type):
            case 'error':
                response = ctypes.windll.user32.MessageBoxW(None, message, title, 0x00040010 | config)
            case 'question':
                response = ctypes.windll.user32.MessageBoxW(None, message, title, 0x00040020 | config)
            case 'warning':
                response = ctypes.windll.user32.MessageBoxW(None, message, title, 0x00040030 | config)
            case 'info':
                response = ctypes.windll.user32.MessageBoxW(None, message, title, 0x00040040 | config)
            case _, 'nothing':
                response = ctypes.windll.user32.MessageBoxW(None, message, title, 0x00040000 | config)
        match (response):
            case 1:
                return 'ok'
            case 2:
                return 'cancel'
            case 3:
                return 'abort'
            case 4:
                return 'retry'
            case 5:
                return 'ignore'
            case 6:
                return 'yes'
            case 7:
                return 'no'
            case 10:
                return 'try-again'
            case 11:
                return 'continue'
            case _:
                return None