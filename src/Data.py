
"""
Data module
Defines data types for Abby.

The base class is Data.
Singular classes are Boolean, Date, String, Number, Nothing, Image, Integer, Link.

A Data object stores the raw data and provides methods for
converting to/from text form and other formats. 

To provide context for a Data object, eg after extracting
it from an Object, wrap it in an Attribute object.

"""

# either put all the formats in here in GetStrings,
# or modularize more...
# leave in here for now


# GetString = Format = Unwrap
#, could pass prop object for hints on how to format it?



import csv
import time
import datetime
import Objects 


import logging
log = logging.getLogger('')
log.debug('loading data.py')


class DataError(Exception):
    """
    Exception for the Data module.
    """
    def __init__(self, arg=None):
        self.arg=arg
    def __str__(self):
        return 'DataError: %s' % str(self.arg)


class Data:
    """
    Base class for extensions to Python data types.
    """
    ## def __init__(self):
        ## raise DataError('__init__ not implemented')
    ## def __repr__(self):
        ## raise DataError('__repr__ not implemented')
    ## def __str__(self):
        ## raise DataError('__str__ not implemented')
    def GetString(self, formattype='human'):
        raise DataError('GetString not implemented')
    def SetString(self, s):
        raise DataError('SetString not implemented')
    ## def GetValue(self):
        ## raise DataError('not implemented')
    
    def GetRawest(self):
        """
        for python types (string, int), rawest version is the python type.
        for our custom types (date, address), rawest version is the
        data object itself. so here in base class define this default behavior.
        python type wrappers should return self.value.
        """
        return self # bool value



#... make persistent?
class Composite(Data,list):
    """
    Stores a list of data objects.
    Can treat as a single data object.
    """
    def __init__(self,value=[],formattype='human'):
#        self.value = value
        list.__init__(self, value)
    
    def __repr__(self):
        #"Data.Composite('%s')" % str(self)
        return list.__repr__(self)

    def __str__(self):
#        return list.__str__(self)
        s = '['
        for data in self:
#            s+=str(data)+','
            s += "'%s', " % data.GetString('human')
        s=s[:-2]
        s+=']'
        return s
        
    def GetString(self, formattype='human'):
        ## if formattype=='human':
            ## return `self.value`
        return `self`

    ## def IsSingleValue(self):
        ## "See if all values in this list are the same"
        ## valueold=self[0].value
        ## for data in self:
            ## if data.value != valueold:
                ## return False
        ## return True

    ## def GetSingleValue(self):
        ## "Get a single value representation of all these values"
        ## if self.IsSingleValue(self):
            ## return '

#    def SetString(self, s):




class Boolean(Data):
    """
    Stores a True/False value.
    """
    def __init__(self,value=False,formattype='human'):
        if isinstance(value, str):            
            #, also handle t, f, 1, 0, yes, no, etc.
            self.value = eval(s.capitalize())
        else:
            self.value = value

    def __repr__(self):
        return "Data.Boolean('%s')" % str(self)

    def __str__(self):
        return `self.value`
        
    def GetString(self, formattype='human'):
        ## if formattype=='human':
            ## return `self.value`
        return `self.value`

    def GetRawest(self):
        return self.value # bool value




class Date(Data):
    """
    Stores a date, allows for more interesting options (?, ca, month year, etc).
    """
    #. merge with date classes from abbyalbum and neomem
    #. allow to store a range of dates also?
    #. or at least have same interface as Dates class?
    # then can treat single date and date ranges the same (eg in css timeline generation)
    
    # class variables (available to all instances)
    #, input is quite rigid now - parser will help
#    formatout = '%a %d %b %Y %I:%M:%S %p'
#    formatout = '%Y-%m-%d' # screw time for now
    formatout = '%Y-%m-%d %I:%M %p'
    asciiFormatOut = '%Y-%m-%d %I:%M:%S %p'
    
    inputformats = [
        '%Y-%m-%d %I:%M:%S %p',
        '%Y-%m-%d',
        '%a %d %b %Y %I:%M:%S %p',
        '%m/%d/%Y %H:%M',
        '%m/%d/%Y %I:%M %p'
        ]
    
    def __init__(self, value=None, formattype='human'):
        """
        Different types of initial values allowed - strings, floating points, etc.
        """
        if value is None:
            self.value = time.time()  # time as floating point
        elif isinstance(value, str):
            self.SetString(value)
        elif isinstance(value, float):
            self.value = value # floating point value
        else:
            raise DataError('Invalid date format')

    def __repr__(self):
        return "Data.Date('%s')" % self.GetString('ascii')

    def __str__(self):
        #, for now, allow value to be a string
        if isinstance(self.value, str):
            return self.value
        else:
    #        time.ctime(self.value)
            #. how far from today is the date?
            #. if close, just show the day of the week... eg Mon
#            today = datetime.datetime.now()
#            days =  datetime.timedelta(
            tuple = time.localtime(self.value)  # convert floating point to tuple
            return time.strftime(Date.formatout, tuple)  # convert to string


    def SetString(self, s):
        """
        Parse string to time.
        """
        #tuple = time.strptime(s, Date.formatin) # convert string to tuple

        #,
        days = ['mon','tue','wed','thu','fri','sat','sun'] # weird order but what weekday() does...
        if s in days:
            dow = days.index(s)
            today = datetime.datetime.now()
            dowtoday = today.weekday()
            if dow < dowtoday:
                dow += 7
            daystoadd = dow-dowtoday
            print 'daystoadd:',daystoadd
            tnew = today + datetime.timedelta(daystoadd)
            print 'tnew:',tnew
            tuple = tnew.timetuple()
            self.value = time.mktime(tuple) # convert tuple to floating point                    
            return #. ahahaha
        
        # default in case other things fail - store date as a string
        self.value = s
        
        for inputformat in Date.inputformats:
            try:
                tuple = time.strptime(s, inputformat) # convert string to tuple
                self.value = time.mktime(tuple) # convert tuple to floating point
                # worked, so break out
                break
            except: #ValueError, e:
                # unrecognized format. try other formats
                # or just leave as a string...
                #self.value = s
                pass
        
            
        
    def GetString(self, formattype='human'):
        #, for now
        if isinstance(self.value, str):
            return self.value
        else:
            tuple = time.localtime(self.value)  # convert floating point to tuple
            if formattype=='ascii':
                s = time.strftime(Date.asciiFormatOut, tuple)
            ## elif formattype=='html':
                ## s = time.strftime(Date.htmlFormatOut, tuple)
            else:
                # default
                s = str(self)
            return s

    ## def GetValue(self):
        ## # eg '2004-08-15 08:15:23 pm'
        ## # better than returning a floating point, which programs would probably
        ## # misinterpret as a float??
        ## return self.GetString('ascii')


## class File(Data):
    ## pass

class Image(Data):
    pass


class Nothing(Data):
    def __init__(self):
        pass
        
    def __repr__(self):
        return "Data.Nothing()"

    def __str__(self):
        return ''

    def GetString(self, formattype='human'):
#        return '(nothing)' # this is nice, except when you do a list command!
        return ''

    def GetRawest(self):
        return None

    def __nonzero__(self):
        return False # (always)



class Number(Data):
    pass


#class Integer(int):
class Integer(Data):
    def __init__(self, value=0, formattype='human'):
        #int.__init__(self, value)
        if isinstance(value, str):
            self.value = int(s)
        else:
            self.value = value

    def __repr__(self):
        return "Data.Integer(%d)" % self.value

    def __str__(self):
#        return str(self)
#        return __builtins__.str(self)
#        return repr(self)
        return str(self.value)
        
    def GetString(self, formattype='human'):
        ## if formattype=='ascii':
            ## s = time.strftime(Date.asciiFormatOut, tuple)
        ## else:
            ## # default
            ## s = str(self)
#        s = str(self)
        s = str(self.value)
        return s

    ## def GetValue(self):
        ## return int(self)
        
    def GetRawest(self):
        return self.value # integer value



class Link(Data):
    """
    Link to an object, or attribute, or file, or folder, or website?...
    """
    def __init__(self, value='', formattype='human'):
        assert(isinstance(value, Objects.Ob))
        self.value = value
    
    def __repr__(self):
        return "Data.Link('%s')" % str(self.value)
        
    def __str__(self):
        return str(self.value)

    def GetString(self, formattype='human'):
        return str(self.value)
        
    def GetRawest(self):
        return self.value # ob reference
    

class LinkFile(Link):
    pass
class LinkObject(Link):
    pass


class String(Data):
    def __init__(self, value='', formattype='human'):
        #str.__init__(self, value)
        if isinstance(value, str):
            if formattype=='asciiNoCR':
                self.value = value.replace('[CR]','\n')
            else:
                # default
                self.value = value
        else:
            self.value = str(value)
            
    def __repr__(self):
        return "Data.String('%s')" % self.value
        
    def __str__(self):
        return self.value

    def GetString(self, formattype='human'):
        if formattype=='ascii':
            #, wrap in double quotes?
#            s = repr(self)
#            s = str(self)
            s = self.value
        elif formattype=='asciiNoCR':
            # format doesn't allow \n's, so replace them with [CR]
            s = self.value.replace('\n','[CR]')
        else:
            # default
#            s = str(self)
            s = self.value
        return s
        

    #def SetString(self, value):
        #pass
    
    ## def GetValue(self):
        ## return str(self)
        
    def GetRawest(self):
        return self.value # string value



#------------------------------------------------------------------------------

def Wrap(value, formattype='human'):
    """
    Wrap a raw value in a Data object.
    if value is already a Data object, just return it.
    formattype is useful for import - eg asciiNoCR 
    """    
    data = value
    ##if isinstance(value, Data):
        ##data = value
    #try:
        # bombs if value is not a class instance! (lame!)
        #if issubclass(value, Data):
            #data = value
    #except:
    if isinstance(value, Data):
        data = value
    elif isinstance(value, str):
        data = String(value, formattype)
    elif isinstance(value, float):
        data = Float(value)
    elif isinstance(value, int):
        data = Integer(value)
    elif isinstance(value, bool):
        data = Boolean(value)
    elif isinstance(value, Objects.Ob):
        data = Link(value)
    elif value==None:
        data = Nothing()
    else:
        raise TypeError(value.__class__)
    return data


def Factory(proptype, propvalue, formattype='human'):
    """
    Create a Data object of the specified type, wrapping the
    given property value.
    eg data = Factory('String', 'hello', 'human')
    """
    assert(proptype) # don't allow empty string here
    assert(proptype!='None')
    s = '%s("""%s""","%s")' % (proptype.capitalize(), propvalue, formattype)
    print 'Factory:',s
    data = eval(s)
    return data



#------------------------------------------------------------------------------

def Test():
    
    list = Composite()
    
    print 'String...'
    data = Wrap('hello!')
    print data
    print data.GetString('ascii') # for ascii file (machine readable)
    print data.GetString('human')
    print data.value
    print repr(data)
    s = 'yeah you know here is a linefeed\nand here is the next line'
    data = Wrap(s)
    print data
    s = data.GetString('asciiNoCR')
    # this should leave the [cr]'s in place
    data = Factory('String',s,'human')
    print data
    # this should convert the [cr]'s to \n's
    data = Factory('String',s,'asciiNoCR')
    print data
    data = Wrap(s,'asciiNoCR')
    print data
    
    print
    list.append(data)
    
    print 'Date...'
    data = Date()
    print data
    print data.GetString('ascii')
    print data.value
    print `data`
    list.append(data)
    data = Date(1092961230.5)
    print data
    list.append(data)
    data = Date('2005-05-03 09:35:23 pm')
    print data
    list.append(data)
    ## data = Date('2005-05-03 9pm')
    ## print data
    ## list.append(data)
    print 'parse "mon"!:'
    data = Date('mon')
    print data
    data = Wrap(data) # should return itself
    print
    
    print 'Integer...'
    data = Integer(5)
    print data
    print data.GetString('ascii')
    print data.value
    print `data`
    list.append(data)
    print
    
    print 'Boolean...'
    #, thinks it's an integer
    data = Wrap(True)
    print data
    print `data`
    list.append(data)
    data = Boolean(True)
    print data
    print `data`
    list.append(data)
    print

    print 'Composite...'
    print list
#    print 'singlevalue?',list.IsSingleValue()
    print

    ## print 'Again...'
    ## list = Composite()
    ## data = Integer(2)
    ## list.append(data)
    ## data = Integer(2)
    ## list.append(data)
    ## print list
    ## print `list`
    ## print 'singlevalue?',list.IsSingleValue()
    ## print
    
    print 'Factory...'
    data = Factory('Date', '2004-08-25 12:35:12pm')
    print data
    print
    
    
    print 'Date...'
    s='4/5/2004 15:24'
    print 'input: ',s
    data = Date(s)
    print 'output:',data
    print
    
    
    print 'done.'
    

if __name__=='__main__':
    Test()
    
    
    
