
#
#	Settings file for the license class.
#

# "COMMANDS:"
# Each flexlm daemon has it's own start-up
# script and runs on it's own port.
# We have to store them here since there's
# really no easy way to figure out which 
# script in /etc/init.d starts which server
COMMANDS = {	'don':{
				7112:'/etc/init.d/license_server',
				27000:'/etc/init.d/adsk_flexlm',
				27001:'/etc/init.d/foundryflexlmserver',
				27002:'/etc/init.d/isllmgrd',
				},
			'tom':{
				1789:'/etc/init.d/nrlmgrd',
				7111:'/etc/init.d/aw_flexlm',
				7112:'/etc/init.d/license_server',
				7113:'/etc/init.d/foundrylmgrd',
				7114:'/etc/init.d/kolektiv_flexlm',
				7489:'/etc/init.d/pixard',
				},
			'ny-server':{
				27000:'license_server',
				27001:'license_server',
				27002:'license_server',
			}
		}

# "GROUPS":
#	Flexlm feature names are cryptic and 
#	redundant since they tend to be 
#	issued in groups based on the purchase.
#	e.g. these are mental ray licenses
#		 (isn't it obvious?)
#		'85400MAYAMMR5_2010_0F',
#		'85400MAYAMMR4_2010_0F',
#		'85400MAYAMMR3_2010_0F',
#		'85400MAYAMMR2_2010_0F',
#		'85400MAYAMMR1_2010_0F',
#
#	This file is used to group feature names
#	under feature 'display' names that will 
#	make sense to us lowly humans that have
#	to use the damn things.
#
_groups = {	
		'Maya Interactive':[
			'85527MAYA_F',
			'85400MAYA_2010_0F',
			],
		'Maya Interactive 2011':[
			'85537MAYA_2011_0F',
			],
		'Maya Interactive 2012':[
			'85694MAYA_2012_0F',
			],
		'Mental Ray':[
			'85530MAYAMMR_F',
			'85694MAYAMMR1_F',
			'85531MAYAMMR1_F',
			'85532MAYAMMR2_F',
			'85532MAYAMMR3_F',
			'85532MAYAMMR4_F',
			'85532MAYAMMR5_F',
			'85400MAYAMMR5_2010_0F',
			'85400MAYAMMR4_2010_0F',
			'85400MAYAMMR3_2010_0F',
			'85400MAYAMMR2_2010_0F',
			'85400MAYAMMR1_2010_0F',
			'85400MAYAMMR_2010_0F',
			'85694MAYAMMR1_2012_0F',
			],
		'Mental Ray 2011':[
			'85537MAYAMMR5_2011_0F',
			'85537MAYAMMR4_2011_0F',
			'85537MAYAMMR3_2011_0F',
			'85537MAYAMMR2_2011_0F',
			'85537MAYAMMR1_2011_0F',
			'85537MAYAMMR_2011_0F',
			],
		'Mental Ray Standalone':[
			'85832MRSTND_F',
			'85831MRSTND_2012_0F',
			],
		'Mental Ray Standalone 2011':[
			'85605MRSTND_2011_0F',
			],
		'Smoke Mac':[
			'85738SMKMAC_F',
			'85737SMKMAC_2012_0F',
			],
		'Smoke Mac Wiretap Gateway':[
			'85737SMKMACWG_F',
			'85738SMKMACWG1_F',
			'85738SMKMACWG2_F',
			'85693SMKMACWG2_2011_0F',
			'85693SMKMACWG1_2011_0F',
			'85737SMKMACWG_2012_0F',
			],
		'Smoke Mac Burn':[
			'85737SMKMACBRN_F',
			'85737SMKMACBRN_2012_0F',
			'85693SMKMACBRN_2011_0F',
			],
		'Mud Box':[
			'70300MBXPRO_F',
			'85696MBXPRO_2012_0F',
			'85580MBXPRO_2011_0F',
			'83900MBXPRO_2010_0F',
			'70200MBXPRO_2009_0F',
			],
		'Maya Fluid Sim':[
			'85529MAYAMFS_F',
			'85537MAYAMFS_2011_0F',
			'85400MAYAMFS_2010_0F',
			],
		'Flame':[
			'flame_x86_64_r',
			'flame_x86_64_r_2011_1',
			'flame_x86_64_r_2012',
			],
		'Flame 2012':[],
		'Flame Premium':[
			'flamepremium_x86_64_r_2011_1',
			'flamepremium_x86_64_r_2012',
			],
		'Smoke':[
			'smokeadvanced_x86_64_r',
			'smokeadvanced_x86_64_r_2012',
			],
		'Smoke 2012':[],
		'Flare':[
			'flare_x86_64_r',
			'flare_x86_64_r_2011_1',
			'flare_x86_64_r_2012',
			],
		'Flare 2012':[],
		'Burn':[
			'burn_x86_64_r_2011_1',
			'burn_x86_64_r',
			'burn_x86_64_r_2012',
			],
		'Wiretap Gateway':[
			'wiretapgw_all_r',
			'wiretapgw_all_r_2011_1',
			'wiretapgw_all_r_2012',
			],
		'discreet L':[
			'discreet_l',
			],
		}

#
#	 the _groups array is built in a
#	 more human readable form but
#	 the license class will need 
#	 to look up the display name (group)
#	 by the feature so we turn the 
#	 _groups array inside out for the
#	 class here...
#
FEATURES = {}
for group,features in _groups.iteritems():
	for feature in features:
		FEATURES[feature] = group

