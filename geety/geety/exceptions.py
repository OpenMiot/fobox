class GeetyException(Exception): ...


class EntryPointNotSet(GeetyException): 
    def __init__(self):
        super().__init__('entry point has not set')


class ComponentAlreadyExists(GeetyException):
    def __init__(self, tag):
        super().__init__(f'component {tag} has redefined twice')
