import re
from A52.utils.stringutil import generate_random_string
#from Crypto.Cipher import Blowfish
import binascii, datetime, time

class InvalidFieldException(Exception):
    def __init__(self, value, validator, rule):
        self.value = value
        self.validator = validator
        self.rule = rule
 
        #if message == None:
        self.message = "'%s' has failed validation: '%s:%s'" % (self.value, self.validator, self.rule)

    def __str__(self):
        return self.message
    
class Field(object):
    def __init__(self, regex=None, required=False, default=None, unique=False, **kwargs):
        self.regex = regex
        self.default = default
        self.required = required

    
    def get_default(self):
        return self.default
    
    def inflate(self, val):
        """
        Called when a AsylumRecord attribute is pulled from the DB
        """
        return val
    
    def deflate(self, val):
        """
        Called before an AsylumRecord attribute is stored in the DB
        """
        return val
    
    def validate(self, val):
        # need to think about how to handle this
        #if self.unique:
        #    pass
        
        if self.required and not val:
            raise InvalidFieldException(val, 'required', None)
            
        if self.regex:
            if re.search(self.regex, str(val)):
                return val
            else:
                raise InvalidFieldException(val, 'regex', self.regex)
        return val


class EncryptedField(Field):
    CRYPT_TAG = '{CRYPT}'
    
    def __init__(self, **kwargs):
        if kwargs.has_key('salt'):
            self.salt = kwargs['salt']
            del kwargs['salt']
        else:
            self.salt = 'hDz3wfCHFGOFOhlm'
        Field.__init__(self, **kwargs)

    def inflate(self, value):
        if self._is_encrypted(value):
            return self._decrypt(value)
        return value
    
    def deflate(self, value):
        if not self._is_encrypted(value) and value != None:
            value = self._encrypt(value)
        return value
        
    def _make_key(self, seed):
        """
        Creates a key for use with Blowfish Ciphers based on salt
        """
        possible = [16,24,32]
        keygen = 'area52fx'
        # if the salt is longer than 32 chars, truncate & return
        key = "%s%s" % (seed, self.salt)
        #key = self.salt
        if len(key) >= possible[-1]:
            return key[:possible[-1]]

        # if it's less than 32 chars, pad appropriately
        for p in possible:
            if len(key) > p:
                continue
            for i in range(len(key),p):
                key += keygen[i%len(keygen)]
            return key

        # This should never happen:
        return None

#    def _generate_seed(self):
#        return ''.join([choice(string.letters + string.digits) for i in range(8)])
    
    def _extract_seed(self, value):
        return value.split('$')[1]

    def _is_encrypted(self, value):
        return str(value)[0:len(self.CRYPT_TAG)] == self.CRYPT_TAG
            
    # NOTe: pass by ref would be faster
    def _quantify_string(self, thing):
        """
        Aligns strings to 8 bytes for encryption.
        'foo' -> '     foo'
        """
        alignment = 8
        return str(thing).rjust((((len(str(thing)) / alignment) + 1) * alignment),' ')

    def _encrypt(self, thing):
        """
        Encrypts the 'thing' based on a key that's based on the username
        """
        thing = self._quantify_string(thing)
        #seed = self._generate_seed()
        seed = generate_random_string(8)
        key = self._make_key(seed)
        #print 'encrypt key = ', key
        obj = Blowfish.new(key, Blowfish.MODE_ECB)
        encrypted = binascii.b2a_hex(obj.encrypt(thing))
        #return self.CRYPT_TAG + encrypted
        return "%s$%s$%s" % (self.CRYPT_TAG, seed, encrypted)
        
    def _decrypt(self, thing):
        """
        Decrypts the 'thing' using the same key that was used for _encrypt
        """
        if thing == None:
            return None
        
        seed = self._extract_seed(thing)
        key = self._make_key(seed)

        start = len(self.CRYPT_TAG) + len(seed) + 2
        thing = thing[start:]

        obj = Blowfish.new(key, Blowfish.MODE_ECB)
        ret = None
        try:
            ret = obj.decrypt(binascii.a2b_hex(thing)).strip()
        except:
            # Should log here
            pass
        return ret
    
class TextField(Field):
    def __init__(self, **kwargs):
        Field.__init__(self, **kwargs)
    
class ChoiceField(Field):
    def __init__(self, choices, **kwargs):
        self.choices = choices
  
        Field.__init__(self, **kwargs)
        
    def validate(self, val):
        if val:
            for k, v in self.choices:
                if str(k) == str(val):
                    return Field.validate(self, val)
            raise InvalidFieldException(val, 'choices', self.choices)
        else:
           return Field.validate(self, val) 
        

    
class CharField(Field):
    def __init__(self, max_length=None, min_length=None, **kwargs):
        self.max_length = max_length
        self.min_length = min_length
        Field.__init__(self, **kwargs)
        
    def validate(self, val):

        if self.max_length:
            if self.max_length < len(str(val)):
                raise InvalidFieldException(val, 'max_length', self.max_length)
            
        if self.min_length:
            if self.min_length > len(str(val)):
                raise InvalidFieldException(val, 'min_length', self.min_length)
     
        return Field.validate(self, val)
    
class IntegerField(Field):
    def __init__(self, min=None, max=None, **kwargs):
        self.min = min
        self.max = max
        Field.__init__(self, **kwargs)
 
    def validate(self, val):
        if val != None:
            try:
                v = int(val)
            except ValueError, e:
                raise InvalidFieldException(val, 'int', 'type')
            
            if self.min != None:
                if self.min > v:
                    raise InvalidFieldException(val, 'min', self.min)
                
            if self.max != None:
                if self.max < v:
                    raise InvalidFieldException(val, 'max', self.max)
            
        
        return Field.validate(self, val)
    
    
#class BooleanField(IntegerField):
#    def __init__(self, **kwargs):
#        self.min = 0
#        self.max = 1
#        Field.__init__(self, **kwargs)
# 
#    def validate(self, val):
#        if val:
#            try:
#                int(val)
#            except ValueError, e:
#                raise InvalidFieldException(val, 'int', 'type')
#            
#            if self.min:
#                if self.min > int(val):
#                    raise InvalidFieldException(val, 'min', self.min)
#                
#            if self.max:
#                if self.max < int(val):
#                    raise InvalidFieldException(val, 'max', self.max)
#            
#        
#        return Field.validate(self, val)
    
class DateField(Field):
    DATE_FORMAT = "%Y-%m-%d"
    
    def __init__(self, auto_create=False, auto_update=False, **kwargs):
        self.auto_update = auto_update
        self.auto_create = auto_create
        Field.__init__(self, **kwargs)
        
    def get_default(self):
        if self.auto_create:
            return datetime.datetime.now().strftime(self.DATE_FORMAT)
        else:
            return None
        
    def inflate(self, val):
        if isinstance(val, str):
            return datetime.date(*time.strptime(val, self.DATE_FORMAT)[0:3])
        return val
    
    
    def deflate(self, val):
        if self.auto_update:
            return datetime.datetime.now().strftime(self.DATE_FORMAT)
        else:
            return val
    
class DateTimeField(DateField):
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    def inflate(self, val):
        if isinstance(val, str):
            return datetime.datetime(*time.strptime(val, self.DATE_FORMAT)[0:6])
        return val
            
    def __init__(self, **kwargs):
        DateField.__init__(self, **kwargs)
        
class DecimalField(Field):
    def __init__(self, min=None, max=None, decimal_places=None, **kwargs):
        self.min = min
        self.max = max
        Field.__init__(self, **kwargs)
#        
#    def validate(self, val):
#        if val:
#            try:
#                dec = decimal.Decimal(val)
#            except ValueError, e:
#                raise InvalidFieldException(val, 'decimal', 'type')
#            
#            if self.min != None:
#                if decimal.Decimal(self.min) > dec:
#                    raise InvalidFieldException(val, 'min', self.min)
#                
#            if self.max != None:
#                if decimal.Decimal(self.max) < dec:
#                    raise InvalidFieldException(val, 'max', self.max)
#                
#        return Field.validate(self, val)

class FloatField(Field):
    def __init__(self, min=None, max=None, **kwargs):
        self.min = min
        self.max = max
        Field.__init__(self, **kwargs)
 
    def validate(self, val):
        if val:
            try:
               v = float(val)
            except ValueError, e:
                raise InvalidFieldException(val, 'float', 'type')
            
            if self.min != None:
                if self.min > v:
                    raise InvalidFieldException(val, 'min', self.min)
                
            if self.max != None:
                if self.max < v:
                    raise InvalidFieldException(val, 'max', self.max)
            
        
        return Field.validate(self, val)
    
