
"""
Objects
(Python didn't like the name Object for this module - got confused)

"""


from persistent import Persistent
from persistent.list import PersistentList

import string # for capwords

import Data
import Layouts

import logging
log = logging.getLogger('')
log.debug('loading objects.py')



def GetInternalName(s):
    # replace spaces with underscores
    #, if this bombs with 'str' object is not callable, it's because s is actually an Obj!
    s = s.replace(' ','_')
    # convert to all lowercase
    return s.lower() 

def GetExternalName(name):
    #, move to object class?
    # replace underscores with spaces
    s = name.replace('_',' ')
    # capitalize each word in string (s.capitalize just does first word)
    return string.capwords(s) 


class Reference(object):
    pass


class Attribute(Reference):

    def __init__(self,obj,prop):
        self.obj = obj
        self.prop = prop
        
    ## def __repr__(self):
        ## return 'Objects.Attribute(...)' # __str__(self)

    def __str__(self):
        return '%s.%s' % (self.obj, self.prop)
            
    def GetObject(self):
        """
        This is part of the Reference interface - gets the object associated with this
        reference object.
        """
        return self.obj
        
    def GetLayout(self, abby, showprops):
        data = self.obj.GetData(self.prop)
        log.debug('getlayout: data=%s' % data)
        s = data.GetString()
        return Layouts.String(s)
        

        ## # return in different layout depending on number of objects
        ## if len(self.ob) > 1:
            ## layout = Layouts.Table(self.abby, self.ob, showprops='all')
        ## else:
            ## layout = Layouts.Properties(self.abby, self.ob, showprops='all') # ie show all properties
            

# base class
# Ob is the interface to Obj and Objs - ie can refer to either a single
# object or a list of objects.
#class Ob(object):
class Ob(Reference):
    def GetObject(self):
        """
        This is part of the Reference interface - gets the object(s) associated with this
        reference object; in this case, itself.
        """
        return self


#class Objs:
#class Objs(Persistent):
#class Objs(Ob, list): # causes problems with objs = Objs()
#class Objs(PersistentList): # bombs
#class Objs(list):
#class Objs(list, Ob): # TypeError: metaclass conflict
#class Objs(Ob, PersistentList.PersistentList):
# this works - just not inheriting from Ob also (but not such a prob in py)
#class Objs(list): 
#class Objs(Ob,list): 
#class Objs(list):
class Objs(PersistentList,Ob):
    """
    Objs stores a list of Obj objects.
    Objs and Obj have a common interface, defined by the Ob class. 
    """
    
    # if you say 
    #    objs = Objs(obj1, obj2)
    # then args will be the tuple (obj1, obj2)
    # and we can pass it to the list constructor
    
    def __init__(self, *args):
#        list.__init__(self, args) # extended list (works)
        PersistentList.__init__(self, args)

        # encapsulated list (works)
#        self.list = PersistentList.PersistentList(args)


    def __repr__(self):
        return 'Objects.Objs(%s)' % self


    def __str__(self):
        if len(self):
            s=''
            delim = ', '
            for obj in self:
                ## print type(obj), obj
#                s += obj.name + delim
                try:
                    s += str(obj) + delim
                except:
                    print 'bomb in objs...'
                    print 's:',s
                    print 'type:',type(obj)
                    print 'obj:',obj
                    raise
            s = s[:-2] #+ '.'
        else:
            s='Empty list'
        return s
#        return str(self.list)


    ## def __len__(self):
        ## return len(self.list)

    ## def Append(self, ob):
        ## self.list.append(ob)

    #, kludge
    def lower(self):
        return str(self) #.lower()

    ## def __getattr__(self, name):
        ## """
        ## Methods/attributes Objs does not know about are delegated to list! 
        ## """
        ## return getattr(self.list, name)

    def GetData(self, prop):
        """
        Will return a Data object (in this case a composite one),
        containing all data associated with these objects.
        """
#        return '(notimp)'
        #. return (multiple values) or single value if all objects have same value!
#        propvalues = []
        datalist = Data.Composite() #,?
        for obj in self:
            data = obj.GetData(prop)
            datalist.append(data)
        ## if propvalues all the same:
            ## s = propvalue
        ## else:
            ## s ='(multiple values)'
        # return string of list of values, eg ['abby', 'neomem']
#        s = `propvalues`
#        s = str(propvalues)
#        return s
        return datalist
        
        
    def SetData(self, prop, data):
        #,, ignore if value is (multiple values), in case user just hit enter
        # on such a string...
        if data=='(multiple values)':
            return
        for obj in self:
            obj.SetData(prop, data)

    #.. move to Layouts.Wrap(ob)
    def GetLayout(self, abby, showprops='all'):# ie show all properties
        if len(self)==1:
            layout = self[0].GetLayout(abby, showprops)
        else:
            layout = Layouts.Table(abby, self, showprops)
        return layout


#,
    ## def Sort(self,property='name',order=1):
        ## """
        ## Sort the objects in this list by the specified property.
        ## """
        ## #. must be a better way...
        ## # eg make a copy of the list, sort it, discard the old one...
        ## # set class properties
        ## Obj.sortby=property
        ## Obj.sortorder=order
        ## self.sort()  # sort list in place
        ## # return to normal
        ## Obj.sortby=''
        ## Obj.sortorder=''



#-----------------------------------------------------------------------------

#class Obj:
#class Obj(Ob):
#class Obj(object):  # default is NOT to use object!!
class Obj(Persistent,Ob):

    def __init__(self,type='',name='',description='', altname=''):
        
        # define base properties
        # don't assign a value unless it contains something (to save space)
        if type: self.type = type
        if name: self.name = name
        if description: self.description = description
        if altname: self.altname = altname
        self.creationdate = Data.Date() # right now
        self.id = 0   # an id will be assigned on adding to db!
        

    def __cmp__(self,other):
        if self.name < other.name:
            return -1
        elif self.name > other.name:
            return 1
        return 0

    ## def __cmp__(self, other):
        ## """
        ## Comparison depends on type of sort set in class variables
        ## Picture.sortby = 'date' or 'uploaddate' or ''
        ## Picture.sortorder = 1 (ascending sort) or -1 (descending sort)
        ## """
        ## if Picture.sortby=='date':
            ## return Picture.sortorder * cmp(self.date, other.date)
        ## elif Picture.sortby=='uploaddate':
            ## return Picture.sortorder * cmp(self.uploaddate, other.uploaddate)
        ## else:
            ## return cmp(self, other)


    # bug: adding this caused zodb and then shelve to bomb with 
    #    TypeError: string is not callable, in copy_reg.py
    # at
    #    dict = getstate()
    # maybe should verify attribute name first?
    # must be relying on some attribute to be either a method or none
    # in this case it's returning '' though, causing it to bomb!
    # but if we want each object to have altname, default being '', how else
    # would we do it?
    def __getattr__(self, name):
        """
        This is called when attribute <name> can't be found.
        So return an empty string. (or could return None)
        but an empty string you can do things with. 
        """
        ## print 'getattr: ',name

        # This is kind of lame - have to add this so that shelve won't think that
        # the empty string is a callable function! 
        #, hopefully can find a better way around this, cause this might slow things 
        # down (gui esp)
        # had to add __getnewargs__ for zodb
        if name in ('__getinitargs__','__getstate__','__setstate__','__getnewargs__'):
            raise AttributeError
        #.. should return Data.Nothing()?
        return ''

    # this didn't work
    ## def __getinitargs__(self):
        ## raise AttributeError
    ## def __getstate__(self):
        ## raise AttributeError
    ## def __setstate__(self):
        ## raise AttributeError


    def __getitem__(self, key):
        """
        Called to implement evaluation of self[key], ie ob[0], so user won't
        know if they have a single object or a list of objects. 
        for loops expect that an IndexError will be raised for illegal indexes to 
        allow proper detection of the end of the sequence. 
        """
        if key==0:
            return self
        raise IndexError        
        
    def __iter__(self):
        """
        Add this so user won't know if they have a single object or 
        a list of objects - can still iterate over its contents by "for obj in ob:"
        Python's generators provide a convenient way to implement the iterator 
        protocol. If a container object's __iter__() method is implemented as a 
        generator, it will automatically return an iterator object (technically, 
        a generator object) supplying the __iter__() and next() methods. 
        """
        yield self # return this object
        raise StopIteration # that's all folks

    def __len__(self):
        return 1


    def __nonzero__(self):
        return True

    def __repr__(self):
        """
        This is called by repr(x), `x`, and >>> x. 
        Ideally, should have eval(repr(x))==x. 
        """
        return "Objects.Obj(%s,%s)" % (`self.type`,`self.name`)
        
        
    def __str__(self):
        """
        This is called by str(x) and print x. 
        """
#        return self.name
        ## assert(isinstance(self.name, str))
        if isinstance(self.name,str):
            return self.name
        else:
            return type(self.name)

    #---------------------------

    ## def Append(self, ob):
        ## # change this object to an Objs list containing self and ob??
        ## pass
        
        
    ## def Delete(self):
        ## """
        ## Delete this object
        ## """


    def GetSize(self):
        """
        Get size of object, in bytes.
        """
        #size is defined as a property
        nsize = len(self.name) + len(self.description)
        return nsize
    # zodb had screwed this up, because it wasn't using new style classes, but v3.3 does!
    size = property(GetSize, doc='Size of object')
    
    ## def getx(self):
        ## return self.__x    
    ## def setx(self, x):
        ## if x < 0: x = 0
        ## self.__x = x
    ## x = property(getx, setx)
    

    #. get proptype (string, number, date, etc) from propdef
    # use proptype to help format data
    # proptype = propdef.propertytype
    def GetData(self, prop):
        """
        Get the property data for the specified property object.
        Returns a Data object. 
        Currently returns Data.Nothing() if property doesn't exist.
        """
        assert(prop.name) # property obj must have a name
        propname = GetInternalName(prop.name)
        try:
            propvalue = self.__dict__[propname]
        except KeyError: # when python can't find a dictionary key
#            return None
            # return empty string? 
            # or i guess the default value for the given property...
            # try the empty string for now...
#            return ''
            ## propvalue = ''
            propvalue = None
        
        # wrap propvalue in a Data object if it isn't already
        # (because strings, ints etc are stored as their python types to save space)
        data = Data.Wrap(propvalue) 
        return data
        
    #.. move to Layouts.Wrap
    def GetLayout(self, abby, showprops='all'): # ie show all properties
        layout = Layouts.Properties(abby, self, showprops) 
        return layout
        
        
    def GetValue(self, propname, formattype='ascii'):
        """
        ascii property interface
        """
        propname = GetInternalName(propname) # make sure it's lower case etc
        try:
            propvalue = self.__dict__[propname] # python type or Data object
        except KeyError: # when python can't find a dictionary key
            # return empty string 
            # or i guess the default value for the given property...
            # try the empty string for now...
            propvalue = ''
        
        if isinstance(propvalue, str):
            return propvalue
        else:
            data = Data.Wrap(propvalue)
            return data.GetString(formattype)
        

    def GetSortValue(self, sortbyprops):
        """
        get a sort string based on a concatenation of the prop objs in sortbyprops list
        """
#            obj.getsortvalue=(obj.getvalue(sortby[0])+...).lower()
        s = ''
        for prop in sortbyprops:
            s = s + str(self.GetData(prop)).lower()
        return s



    def PutIn(self, adjectives):
        """
        Put this object in the given sets (adjectives).
        eg 'put alarmclock in kalispell' == 'alarmclock.company=kalispell'
        """
        if adjectives:
            for adj in adjectives:
                # adj is just an object, eg 'math'
                #, property names should always be lowercase!
                #. use InternalName?
                propname = adj.type.lower()  # eg 'subject'
                #. and of course this will become a Link object (?)
                propvalue = adj.name   # eg 'math'
                log.debug ('setting %s to %s' % (propname,propvalue))
                self.SetValue(propname, propvalue)


# 
    def SetData(self, prop, data):
        """
        Store the given data in this object under the given property.
        """
        #. yuck - must pass data=Data.Nothing() to delete the property
        assert(prop.name) # property obj must have a name
        assert(isinstance(prop, Ob))
        assert(isinstance(data, Data.Data)) # data must be a Data instance
        propname = GetInternalName(prop.name)
        ## #, kludge
        ## proptype=str(proptype).lower()
        ## if proptype=='dateproptype': proptype='Date'
        ## if proptype=='none': proptype=None
        if isinstance(data, Data.Nothing):
            # if data is Nothing, just delete the existing property value
            if self.__dict__.has_key(propname):
                self.__dict__.pop(propname)
        else:
            # don't want to use Data for python types, eg strings, ints
            value = data.GetRawest() 
            self.__dict__[propname] = value  # Data obj or python type
        self._p_changed = 1 #, zodb doesn't seem to recognize a changed dictionary...

        #, broadcast this message
        #return 'set %s to %s' % (propname, str(data))


    def SetValue(self, propname, propvalue):
        """
        ascii interface
        """
        # make sure propname is lowercase!
        propname = GetInternalName(propname)
        
        if propvalue:
            #. not good - don't know what kind of crap the user is passing
            # need to make sure it's a Data object or python type at least.
            # eg parser screws up and gives an Objs to the command, which hands it here...
            data = Data.Wrap(propvalue)
            value = data.GetRawest() 
            self.__dict__[propname] = value
        else:
            # if propvalue is empty, just delete the existing property value
            if self.__dict__.has_key(propname):
                self.__dict__.pop(propname)
        self._p_changed = 1 #, zodb doesn't seem to recognize a changed dictionary...
        
        #, broadcast this message
        #return 'set %s to %s' % (propname, propvalue)


    def sort(self, f):
        # can just ignore this since only one object in this 'list'!
        pass


    # propdef methods...
    
    ## def Unwrap(self, data):
        

#-----------------------------------------------------------------------------


## class PropDef(Obj):
    ## """
    ## A property definition object. Has some special methods...?
    ## """




## def MakeOb(list):
    ## """
    ## Make an Ob object, which is an Obj object or Objs object, depending
    ## on the number of Objs in the list. 
    ## Both Obj and Objs have the same interface, so can be used interchangeably.
    ## If list is empty, will return an empty Objs list.
    ## """
    ## n = len(list)
    ## if n==0:
        ## ob = Objs()  # empty objs list
    ## elif n==1:
        ## ob = list[0] # get only Obj from list
    ## else:
        ## ob = Objs() # create empty Objs list
        ## ob.extend(list)  # extend it by adding the Objs in the list 
        ## # not append - that appends the entire list as one item!
    ## return ob


#-----------------------------------------------------------------------------


## import unittest
## class TestObjects(unittest.TestCase):    

def Test():

    import Abby
    import Commands
    import Streams
    import Layouts
    
    #.. ditch abby from the tests!!!
    
    filename = 'test.abby'
    abby = Abby.Abby()
    abby.Open(filename, False)

    print 'Get equations...'
    rs = abby.Get(type='equation')
    print rs
    print Layouts.Table(abby, rs)
    print
    
    print 'get desc'
    rs = abby.Get(id=1012)
    obj = rs[0]
    desc = obj.GetValue('description')
    print desc
    assert(desc=='iawjiejlijij')
    print

    s = 'creation_date'
    print s
    s = GetExternalName(s)
    print s
    s = GetInternalName(s)
    print s
    print
    
    print 'test desc'
    obj = Obj('Project','abby')
    print 'obj:',obj
    obj.SetValue('desc','laiwjelai jwlei ajlwij e')
    s = obj.GetValue('desc')
    print s
    print
    
    obj = Obj('Project','neomem')
    print 'obj:',obj
    propId = Obj('property','id')
    data = obj.GetData(propId)
    print 'obj.id:',data
#    print type(data) #, why gives 'instance' instead of actual classname??
    print 'data.__class__:',data.__class__
    propName = Obj('property','name')
    data = obj.GetData(propName)
    print 'obj name:',data
    print

    print 'Test extend...'
    rs = abby.Get(id=1001)
    rs2 = abby.Get(id=1002)
    rs.extend(rs2)
    print rs
    print

    
    abby.Close(False)  # lose all changes



if __name__=='__main__':
    Test()
    
    
