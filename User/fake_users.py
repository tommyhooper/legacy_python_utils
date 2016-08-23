

# A Dict of 'fake' users...
# There are a few 'utility' users that are helpful
# and not necessary to have existing in the AD database.
# e.g. The engineering users that should exist in several departments
# e.g. A fallback user in case the AD server dies.

fake_users = {'discreet':[],
		'engineering':[],
		'design':[],
		'all':[]
		}

# define the users first
beam = {
		'user_id':'beam',
		'cn':'Jim Beam',
		'data' : {
			 'cn' : ['Jim Beam2'],
			 'name' : ['Jim Beam2'],
			 'department' : ['unknown'],
			 'displayName' : ['JB'],
			 'givenName' : ['Jim'],
			 'sAMAccountName' : ['beam'],
			 'sn' : ['beam'],
			 'title' : ['engineer'],
			 'userPrincipalName' : ['eng@a52.com'],
			 'primaryGroupID' : ['101'],
			 'distinguishedName' : ['CN=Jim Beam,OU=staff,OU=a52,DC=a52,DC=com'],
			 'accountExpires' : ['9223372036854775807'],
			 'badPasswordTime' : ['0'],
			 'badPwdCount' : ['0'],
			 'codePage' : ['0'],
			 'countryCode' : ['0'],
			 'instanceType' : ['4'],
			 'lastLogoff' : ['0'],
			 'lastLogon' : ['0'],
			 'logonCount' : ['0'],
			 'objectCategory' : ['CN=Person,CN=Schema,CN=Configuration,DC=a52,DC=com'],
			 'objectClass' : ['top', 'person', 'organizationalPerson', 'user'],
			 'pwdLastSet' : ['129141147561908750'],
			 'sAMAccountType' : ['805306368'],
			 'uSNChanged' : ['1765163'],
			 'uSNCreated' : ['78866'],
			 'userAccountControl' : ['66050'],
			 'whenChanged' : ['20110328010631.0Z'],
			 'whenCreated' : ['20100326220556.0Z']
			 }
		 }

# Add the users to the departments
fake_users['discreet'].append(beam)
fake_users['engineering'].append(beam)
fake_users['design'].append(beam)
fake_users['all'].append(beam)
