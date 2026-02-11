import sys, importlib
if 'fobox.app' not in sys.modules.keys():
    from fobox.app import dp
else:
    dp = importlib.reload(sys.modules['fobox.app']).dp
