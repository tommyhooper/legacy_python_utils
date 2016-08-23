
from libwiretapPythonClientAPI import *
WireTapClientInit()
server = WireTapServerHandle('flaretest')
print server.ping(1)
print server.lastError()

