import time

name = 'FactorioError' # For log

class ErrorFixed(Exception):
    pass
class FactorioError (Exception):
    FileManagerFail = {
        'id': 'FileManagerFail',
        'isfatal': True
    }
    ConnectionError = {
        'id': 'ConnectionError',
        'isfatal': True,
        'showPopupWindow': False
    }
    LostConnectionError = {
        'id': 'LostConnectionError',
        'isfatal': True,
        'showPopupWindow': False
    }
    SomeoneAlreadyPlaying = {
        'id': 'SomeoneAlreadyPlaying',
        'isfatal': True
    }
    def __new__(cls, *args):
        error = args[0]
        error_isfatal = error.get('isfatal', True)
        if error_isfatal:
            if cls.repair(args):
                return ErrorFixed()
            else:
                return super().__new__(cls, args)
        else:
            #threading.Thread(target=cls.repair, args=error_name)
            return ErrorFixed()
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        
    
    @staticmethod
    def repair (*args) -> bool:
        """Intenta reparar una excepcion.
        ## Args
        args[0]: está reservado para el id de error."""
        args = args[0] # Don't remove
        error_name = args[0].get('id', None)
        match (args[0]):
            case FactorioError.ConnectionError:
                args[1].logger.info(f'Fixing error. ID: {error_name}', name)
                for i in range(10):
                    if args[1].online:
                        args[1].logger.debug(f'Error fixed. ID: {error_name}', name)        
                        return True
                    time.sleep(1)
                args[1].logger.error(f'Couldn\'t fix error. ID: {error_name}', name)
                return False
            case FactorioError.LostConnectionError:
                return False
            case FactorioError.SomeoneAlreadyPlaying:
                return False
            case _:
                return False