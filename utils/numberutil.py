
#import decimal
import string
import re
import math

#HOURS_PER_DAY = decimal.Decimal("8.00")

def numbers_only(value):
	"""
	Strip non-numeric characters out
	of 'value'
	"""
	return string.join(re.findall(r'[0-9.]+',value),'')

def scale_bytes(num,input_scale='b',output_scale='G',return_int=True):
	"""
	Convert 'num' (bytes) to a specific
	scale: ['b','kb','M','G','T','P']
	"""
	key = ['b','kb','M','G','T','P']
	# let the input and output scaling cancel
	# each other out so we only have to calculate
	# what is necessary
	scale = key.index(output_scale) - key.index(input_scale)
	for i in range(0,abs(scale),1):
		if scale > 0:
			num = num / 1024.00
		else:
			num = num * 1024
	if return_int:
		return int(round(num,0))
	return num

def humanize(num,scale='kilobytes'):
	"""
	Convert 'num' to a human readable form
	"""
	r = 0
	while num > 1000:
		num = num / 1024.00
		r+=1
	if scale == 'bytes':
		key = ['b','kb','M','G','T','P']
	if scale == 'kilobytes':
		key = ['kb','M','G','T','P']
	# human rounding: above 10G we generally
	# start thinking in whole numbers, however
	# with Terabytes the fraction becomes
	# important again.
	if key[r] == 'T':
		return "%s%s" % (round(num,2),key[r])
	elif key[r] == 'G':
		if num > 10:
			return "%s%s" % (int(round(num,0)),key[r])
		else:
			return "%s%s" % (round(num,1),key[r])
	else:
		return "%s%s" % (int(round(num,0)),key[r])

def humanize_test(size,scale=None):
	if (size == 0):
		return '0B'
	size_name = ("KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
	i = int(math.floor(math.log(size,1024)))
	p = math.pow(1024,i)
	s = round(size/p,2)
	return '%s %s' % (s,size_name[i])

#def accounting_format(num, precision='0.01'):
#    if num == None:
#        return decimal.Decimal('0.00')
#    return decimal.Decimal(str(num).strip()).quantize(decimal.Decimal(precision), rounding=decimal.ROUND_HALF_UP)

#def _hours_to_days(hours):
#    days = decimal.Decimal(hours) / HOURS_PER_DAY
#    return accounting_format(days)
#
#def _days_to_hours(days):
#    hours = decimal.Decimal(days) * HOURS_PER_DAY
#    return accounting_format(hours)

def safe_divide(num, den):
    if den > 0:
        
        rate = num / den
    else:
        rate = 0
            
    return rate

#def sum_accounting_stats(stat_models):
#    """
#    Takes a list of stat_models (as returned by bid.get_accounting_bs(),
#    sums the following fields:
#     actuals['hours'], actuals['cost'], estimates['hours'], estimates['cost']
#    NOTE: This summation only happens when two or more entries in have the same common_key
#    """
#    tmp = {}
#
#    for stat_model in stat_models:
#
#        model = stat_model['model']
#        actuals = stat_model['actuals']
#        estimates = stat_model['estimates']
#        
#        id = model.pk
#
#        if not tmp.has_key(id):
#            tmp[id] = stat_model
#        else:
#            tmp[id]['actuals']['cost'] += accounting_format(actuals['cost'])
#            tmp[id]['actuals']['hours'] += accounting_format(actuals['hours'])
#            tmp[id]['estimates']['cost'] += accounting_format(estimates['cost'])
#            tmp[id]['estimates']['hours'] += accounting_format(estimates['hours'])
#            
#    return tmp.values()
    
def calculate_accounting_stats(actual, bid=None):
    my_dict = {}
    my_dict['actual_hours'] = actual['hours']
    my_dict['actual_cost'] = actual['cost']
    #my_dict['actual_rate'] = actual['rate']
    
    my_dict['bid_hours'] = accounting_format(0)
    my_dict['bid_cost'] = accounting_format(0)
    #my_dict['bid_rate'] = accounting_format(0)
    
    if bid:
        my_dict['bid_hours'] = bid['hours']
        my_dict['bid_cost'] = bid['cost']
        #my_dict['bid_rate'] = bid['rate']
    
    my_dict['bid_rate'] = accounting_format(safe_divide(my_dict['bid_cost'], my_dict['bid_hours']))
    my_dict['actual_rate'] = accounting_format(safe_divide(my_dict['actual_cost'], my_dict['actual_hours']))
    
    # handle edge cases
    if my_dict['bid_cost'] == 0 and my_dict['actual_cost'] == 0:
        my_dict['estimated_cost'] = accounting_format(0)
        my_dict['estimated_profit'] = accounting_format(0)
    elif my_dict['bid_cost'] == 0 and my_dict['actual_cost'] > 0:
        my_dict['estimated_cost'] = my_dict['actual_cost']
        my_dict['estimated_profit'] = accounting_format(-1*my_dict['estimated_cost'])
    elif my_dict['bid_cost'] > 0 and my_dict['actual_cost'] == 0:
        my_dict['estimated_cost'] = my_dict['bid_cost']
        my_dict['estimated_profit'] = accounting_format(0)
    else:
        if my_dict['actual_cost'] > my_dict['bid_cost']:
            my_dict['estimated_cost'] = my_dict['actual_cost']
        else:
            my_dict['estimated_cost'] = accounting_format(safe_divide((my_dict['actual_cost'] * my_dict['bid_hours']), my_dict['actual_hours']))
        
        my_dict['estimated_profit'] = accounting_format(my_dict['bid_cost'] - my_dict['estimated_cost'])
        
    return my_dict
    #dict['estimated_cost'] = accounting_format(dict['actual_rate'] * (dict['bid_hours'] - dict['actual_hours']) + dict['actual_cost'])
      
if __name__ == '__main__':
	#humanize(7735043584)
	#print humanize(313345920,scale='kilobytes')
	print scale_bytes(4636329472,input_scale='kb',output_scale='b')


