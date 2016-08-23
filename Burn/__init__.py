""" A52 Module """

#__version__ = "$Revision: 1.13 $".split()[-2:][0]

from main import Burn


# Burn object map:
"""

There are a couple of contexts to view burn information from:

1. Job context. This is the most important since it's primarily
   what we end up wanting in practice. 

   i.e. focus on a burn job and see which nodes have been and are 
   processing it, then show the logs for those nodes. Also parse the logs
   and show the relevant information like 'errors', 'start time' etc...

2. Node context. This could be useful to see what all the nodes are doing
   at a given time... or something else useful which I can't think of yet

3. Backburner context. This would be the overview of all the jobs, their
   status, start time, stop time, time per frame. Basically the information
   that is counter intuitively laid out in the Discreet backburner page.


Objects:
	Burn (Backburner)
		Burn.jobs

	BurnJob
		BurnJob.nodes

	BurnNode
		BurnNode.log
		BurnNode.restart()
		BurnNode.reboot()










"""
