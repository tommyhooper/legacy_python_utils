
import sys
sys.path.append('/usr/discreet/flamepremium_2012.SP2/python')
sys.path.append('/usr/discreet/flame_2012.SP2/python')
from libwiretapPythonClientAPI import *

"""
	    Host:	flame01
        Volume:	stonefs4
	 Project:	11A219-Nike_BB_Never_Ends_CamCoombs
 	 Library:	Default
	    Clip:	NIKE_ROF_030.0002_ff_CS_Left_billboard_corona
	  'node':	<libwiretapPythonClientAPI.WireTapNodeHandle object at 0x2b5ad4c64a48>,
	  'type':	'CLIP',
	  'name':	'NIKE_ROF_030.0002_ff_CS_Left_billboard_corona',
	'nodeID':	'/stonefs4/11A219-Nike_BB_Never_Ends_CamCoombs/Default/H_-1463759519_S_1319078511_U_25105/H_-1463759519_S_1319078511_U_25236'}

	flame01 segfault:
	  node.lastError(): Connection reset by peer
	  /usr/discreet/sw/sw_wiretapd: line 53: 25068 Segmentation fault      $server_prog -c /usr/discreet/wiretap/cfg/wiretapd.cfg $*

	flame04 segfault:
	  node.lastError(): Connection reset by peer
	  /usr/discreet/sw/sw_wiretapd: line 53: 26155 Segmentation fault      $server_prog -c /usr/discreet/wiretap/cfg/wiretapd.cfg $*

"""

original = {	'server':'flame01',
			'nodeID':'/stonefs4/11A219-Nike_BB_Never_Ends_CamCoombs/Default/H_-1463759519_S_1319078511_U_25105/H_-1463759519_S_1319078511_U_25236'}
duplicate = {	'server':'flame04',
			'nodeID':'/stonefs4/11A197-Diet_Coke_Studio_MASTER/Default/H_-899569472_S_1320970667_U_59289'}

server = WireTapServerHandle(duplicate['server'])
node = WireTapNodeHandle(server,duplicate['nodeID'])
metaData = WireTapStr()

## NOTE: The getMetaData call causes the segfault!
if not node.getMetaData("DMXEDL","",256,metaData):
	print "ERROR:",node.lastError()
else:
	metaDataList = metaData.c_str().split("\n")
	print "MDL:",metaDataList
