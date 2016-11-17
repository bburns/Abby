
"""
Abby
Defines the Abby database object, which uses ZODB to persist objects.

Requires ZODB http://www.zodb.org/

"""



# Python modules
import os.path
#import shelve # for AbbyShelve


# Zodb modules
# Because of some special magic that ZODB does, you must first import ZODB 
# before you can import Persistent. The Persistent module is actually created 
# when you import ZODB.
import ZODB
from ZODB import FileStorage, DB
#from Persistence import Persistent # zodb!
# #from ZODB import PersistentList
from persistent import Persistent
import transaction



# Set up logging (move to module?)
import logging
import logging.handlers
import sys
## logging.basicConfig()
## log = logging.getLogger("Villa")
## log.setLevel(logging.DEBUG) #set verbosity to show all messages of severity >= DEBUG
## log.info("Starting Villa")
## handler = logging.handlers.

# set up logging to stdout
#logging.basicConfig()
log = logging.getLogger('')
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)
#logger.setLevel(DEBUG)
#log = logging.getLogger('Abby')
#log = logging.getLogger('')
#log.setLevel(logging.DEBUG) # set verbosity to show all messages of severity >= DEBUG
log.setLevel(logging.INFO) # set verbosity to show all messages of severity >= DEBUG

# set up logging to logfile
formatter = logging.Formatter('%(asctime)s  %(name)-18s %(levelname)-8s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S')
logname = 'VillaDebugLog.txt'
logfile = logging.handlers.RotatingFileHandler(logname, 'w', 100000, 0) # w=write,a=append; maxsize
#?logfile = logging.handlers.FileHandler(logname, "a") 
logfile.setFormatter(formatter)
log.addHandler(logfile)

# define a Handler which writes messages to the sys.stderr (screen)
## console = logging.StreamHandler()
## console.setLevel(logging.DEBUG) #INFO)
## formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
## console.setFormatter(formatter)
## log.addHandler(console)

log.debug('')
log.debug('loading abby.py')




# Abby modules
import Objects
#import Commands
import Data
import Layouts



class AbbyError(Exception):
    def __init__(self, arg=None):
        self.arg=arg
    def __str__(self):
        return 'AbbyError: %s' % str(self.arg)
    
## class AbbyWarning(Exception):
    ## def __init__(self, arg=None):
        ## self.arg=arg
    ## def __str__(self):
        ## return 'AbbyWarning: %s' % str(self.arg)



class Abby(object):
    
    def __init__(self, debug=False):
        
        self.SetDebug(debug)
        
        log.debug('abby init')
        
        self.filename = ''
#        self.nextid = 1000
#        self.wordindex={}

        self.version = '0.1'
        self.status = 'Initializing' # current status string
        self.it = None # current obj or objs
#,        self.commandhistory = Commands.History()
  
        # zodb
        self.storage=None
        self.db = None
        self.connection = None
        self.rootdict = None  # disk-based dictionary        

        # default layout
        #, put this here?
        #self.layoutDefault = Layouts.Table(self)


    def __len__(self):
        return len(self.rootdict)

   
    def Open(self, filename, createfile=False):
        """
        Open the specified database file.
        Get type of database from extension (eg ini, mdb, txt, filesys)...
        """

        self.filename = filename

        # create zodb
        # ** ZODB supports many pluggable storage back-ends, eg FileStorage, which 
        # stores your object data in a file. Other storages include storing objects in 
        # relational databases, Berkeley databases, and a client-to-server storage, 
        # which stores objects on a remote storage server.
        self.storage = FileStorage.FileStorage(filename, create=createfile)
        self.db = DB(self.storage)
        self.connection = self.db.open()
        
        # The root object is the dictionary that holds all of your persistent objects.
        self.rootdict = self.connection.root()

        # shelve
        if createfile:
            self.docobj = Objects.Obj('system','docobj', 'stores document properties')
            self.docobj.id = 100
            self.docobj.nextid = 1000
            self._AddToIndex(self.docobj)  # adds to self.rootdict dictionary
            ## self.rootdict = shelve.open(filename,'c')
            ## # assign our (new) objects to the database
## #            self.rootdict['nextid'] = self.nextid
## #            self.rootdict['objects'] = self.objects
## #            self.rootdict['wordindex'] = self.wordindex
            self.status="Created database %s." % filename
        else:
            # get our document object
            self.docobj = self.rootdict[100]
            ## self.rootdict = shelve.open(filename)
            ## # read our objects from database
            ## # these are just references to the objects that are stored in the database
            ## #, so presumably won't cause any problems by doing this...?
## #            self.nextid = self.rootdict['nextid']
## #            self.objects = self.rootdict['objects']
## #            self.wordindex = self.rootdict['wordindex']
            self.status="Opened database %s." % filename



    def Add(self, type='', name='', description=''):
        """
        Create a new object and add it to the database.
        Returns the new object.
        Will raise exception on failure.
        """
        
        log.debug('add type=%s name=%s desc=%s' % (type,name,description))
        
        #, raise error if name already exists
        obj = self.Get(exactname=name)
        if obj:
            raise AbbyError("An object named '%s' is already in the database." % name)
            
        # create object
        obj = Objects.Obj(type, name, description)

        return self._AddToIndex(obj)
        
        
    def _AddToIndex(self, obj):
        """
        Add the specified object to the index, using a unique number as the id.
        Hidden because user should never be able to create an object on their own,
        should only do it through the Add factory method.
        But need this for Undo handling, Import, etc.
        """
        # assign a unique id if object doesn't have one yet
        if obj.id == 0:
            obj.id = self._GetNextId()

        #, writeover flag to allow writing over exiting objects?
        assert(self.rootdict.has_key(obj.id)==False)

        # add object to main dictionary
        self.rootdict[obj.id] = obj

        #, add name to name and type indexes also
        # kiss - don't use index until db size gets unwieldly
        ## if self.wordindex.has_key(name):
            ## # word already exists in index, so add this object to a list of objects
            ## print name,'already in wordindex!'
            ## ob = self.wordindex[name]
            ## #ob.Append(obj) # polymorphic append to Obj or Objs!?
            ## if type(ob) == type(Objects.Objs):
                ## print 'appending obj to existing objs'
                ## ob.Append(obj)
            ## else:
            ## print 'creating Objs(ob, obj)'
## #            ob = Objects.Objs(ob, obj)
## #            print ob
## #            print isinstance(ob, type(Objects.Objs))
            ## print 'assigning new/updated ob to wordindex'
            ## self.wordindex[obj.name] = ob
        ## else:
            ## print 'adding obj to wordindex as new entry'
            ## self.wordindex[obj.name] = obj            

        # again, don't do this here!
#        self.it = obj # set current object

#        self.status = "Added object '%s'." % obj.name

        # return newly created object to user
        return obj


    def Close(self, savechanges=True):
        """
        Close the database.
        """

        if savechanges:
            print 'Closing abby database, saving changes...'
            ## transaction.commit()
            self.Save()
        else:
            print 'Closing abby database, discarding all changes since last save...'
            # abort the transaction. useful for testing by adding junk to db. 
            transaction.abort()
            
        # zodb
        self.connection.close()
        self.db.close()
        self.storage.close()
        #. could also delete any leftover files, since they don't seem to be
        # needed... (though index may as file grows?)
        # stuff.fs.index, .lock, .tmp
        print 'Abby database closed.'


    def Delete(self, ob): #=None, id=None):
        """
        Delete the specified object(s).
        """
        name = str(ob)
        #. more likely, set flag in object so it's deleted (so can undelete later)
        for obj in ob:
            id = obj.id
            obj = self.rootdict.pop(id)
            assert(obj.id == id) # make sure object we removed was indexed correctly at least
        #. update status text
        # note: cmd object returns a string which console will print out
#        self.status = "Object '%s' deleted." % name
        # don't do this here
#        self.it = None # clear current object


    def Find(self, s):
        """
        Find all occurrences of the given string, returning a list of Hit objects.
        Search through all objects and their properties. 
        """
        #. do case-insensitive
        #. handle > find olk in words, ie restrict by adj also
        list = Data.List()
        for obj in self.rootdict.itervalues():
            for prop in obj:
                if s in prop:
                    attrib = Attrib(obj, prop)
                    hit = Hit(attrib) #,location or occurrence?)
                    list.append(hit)
        return list
        
        # 
        
        
        
    def Get(self, name=None, type=None, id=None, afilter=None, exactname=None):
        """
        Get a recordset (Objs) containing Objects that match the specified criteria.
        Pass nothing to get list of all objects.(?)
        afilter is a Comparisons object that provides a GetFilterFunction() method.
        This function may raise an exception, eg if id not found in database.
        """
        
        # this should always return an objs list (which functions as a recordset, for now)

        #. best to add each condition as a function?
        # eg fn = lambda obj: obj.name=='tolkein'

        ob = Objects.Objs()  # default: empty objects list
        
        if id:
            # get the object with the specified id
            obj = self.rootdict[id]
            ob.append(obj)
            
        elif name:
            # get list of all objects with specified name
            name = name.lower()
            for obj in self.rootdict.itervalues():
                if (name in obj.name.lower()):
                    ob.append(obj)
                #, check in any other 'name' properties, eg 'altname', 'symbol', 'code'...?
                elif (name in obj.altname.lower()):
                    ob.append(obj)
            
        elif exactname:
            # get single object with specified name
            #, get best pick (based on popularity)
            exactname = exactname.lower()
            for obj in self.rootdict.itervalues():
                if (exactname == obj.name.lower()):
#,                if (exactname == Lower(String(obj.GetProp('type')))
                    ob.append(obj)
                    break
                #, check in any other 'name' properties, eg 'altname', 'symbol', 'code'...?
                elif (exactname == obj.altname.lower()):
                    ob.append(obj)
                    break
            
        elif type:
            # get list of all objects with specified type
            type = type.lower()
            for obj in self.rootdict.itervalues():
                if (type in obj.type.lower()):
                    ob.append(obj)
        
        elif afilter:
            # get list of all objects that match the given filter object.
            # iterates over all values (ie obj objects) in the root dictionary,
            # and returns a list for which the given fn is true. 
            list = filter(afilter.GetFilterFunction(), self.rootdict.itervalues())
            ob.extend(list)
            
        else:
            # get a list of all the objects in the db
            for obj in self.rootdict.itervalues():
                ob.append(obj)
        
#        self.status = 'Ready'        
#        return None
        # don't do this here, because Get is called by the tokenizer, which
        # scrambles the IT value!
#        self.it = ob # set current object

        # ob might be empty objects list
        return ob


    def _GetNextId(self):
        ## id = self.nextid
        ## self.nextid = id + 1
        ## self.rootdict['nextid'] = self.nextid # update database also
        id = self.docobj.nextid
        self.docobj.nextid = id + 1
        return id



    ## def Put(self, ob):
        ## """
        ## Put the given object(s) back onto the shelf (ie write it back to the database).
        ## This must be called after any changes are made to an object!
        ## """
        ## for obj in ob:
            ## self.rootdict[obj.id] = obj


    def RebuildIndexes(self):
        """
        Rebuild all indexes, in case they have gotten out of whack.
        """
        pass
        # just the word index for now


    def Save(self):
        """
        Commit all pending transactions to the database.
        """
        ## Save all dirty objects to the database.
        # you can think of committing transactions as checkpoints where you save 
        # the changes you've made to your objects so far. 
#        print "saving abby database..."
        transaction.commit()
#        self.status = 'Transactions committed'
#        self.status = 'File %s saved.' % self.filename

        ## # how do you get list of all objects in memory?
        ## # this just unpickles each object from the db, overwriting 
        ## # whatever is in memory!
        ## for id,obj in self.rootdict.iteritems():
            ## if obj.dirty:
                ## self.rootdict[id] = obj
        ## self.status = "File '%s' saved." % self.filename


    def SetDebug(self, debug):
        self.debug = debug # save flag
        # set logging output level
        if debug:
            log.setLevel(logging.DEBUG)
        else:
            log.setLevel(logging.INFO)


    def Verify(self, fix=True):
        """
        Verify database integrity and correct any mistakes.
        """
        
        assert(fix) # for now
        
        ## fix = False
        
        #, make this all more modular, ie each test as a fn or class
        
        checkids = False#True
        checkdata = False#True
        checkdates = False#True
        checkaltnames = False#True
        checknames = True
        
        # make sure id values are correct
        nids=0
        if checkids:
            print 'checking id values...'
            prop = self.Get(exactname='Id')
            for id, obj in self.rootdict.iteritems():
                # make sure key is an integer, not a string
                if not isinstance(id, int):
                    print '%s has noninteger key' % obj
                    nids += 1
                    if fix:
                        # change to int
                        self.rootdict.pop(id)
                        id = int(id)
                        self.rootdict[id]=obj
                # make sure key matched object id
                if id != obj.id:
                    print '%s filed incorrectly' % obj
                    nids += 1
                    if fix:
                        print ' - changing obj.id from %s to %d...' % (str(obj.id), id)
                        obj.SetData(prop,Data.Wrap(id))
                    
        # check data types and convert to raw values, since it's wasteful
        # to store a whole Data object when a raw python type will do!
        ntypes=0
        if checkdata: 
            print 'checking data types...'
            for obj in self.rootdict.itervalues():
                for propname, data in obj.__dict__.iteritems():
                    propname = Objects.GetExternalName(propname)
                    prop = self.Get(exactname=propname)
                    isbad = isinstance(data, Data.String) or isinstance(data, Data.Integer)
                    if isbad:
                        print 'Found Data object in %s.%s' % (obj,prop)
                        ntypes += 1
                        if fix:
                            # convert to raw python type
                            #obj.__dict__[propname] = propvalue.GetRawest()
#                            obj.SetValue(propname, propvalue.GetRawest())
                            obj.SetData(prop, data)
                    #ispythontype = isinstance(propvalue, str) or isinstance(propvalue, int) or isinstance(propvalue, float)
                    #if not (issubclass(propvalue, Data.Data) or ispythontype):
                        ## ie data is not a correct type... kill it!
                        #print 'bad data type found in %s.%s' % (str(obj.name),propname)
                        #print 'value: ', propvalue
                        #s = input('ok to kill value?')
                        #ntypes += 1
                        
        # check date properties
        ndates = 0
        if checkdates:
            print 'checking date properties...'
            for obj in self.rootdict.itervalues():
                #, hardcode props to search for now - later go by proptype=date
                propnames = ['creationdate','date','finaldate']
                for propname in propnames:
                    prop = self.Get(exactname=propname)
                    data = obj.GetData(prop) # get Data object
                    if data:
                        isdate = isinstance(data, Data.Date)
                        if isdate:
                            #data.Verify()
                            if data.value=='':
                                ndates+=1
                                print 'blank date in %s.%s=%s' % (obj,prop,data)
                                if fix:
    #                                obj.SetData(prop,Data.Nothing()) # delete the property
                                    obj.SetValue(propname,'') # delete the property
                            if isinstance(data.value, str):
                                ndates+=1
                                s = data.value
                                print 'string date in %d.%s=%s' % (obj.id,prop,s)
                                if fix:
                                    data.SetString(s)
                                    print ' - new value:',data
                                    obj.SetData(prop,data) # save to db
                                else:
                                    print
                        else:
                            print 'bad date property (ie not a Data.Date) in %s.%s=%s' % (obj,prop,data)
                            ndates+=1
                            if fix:
                                s = str(data) # make sure we're starting with a string!
                                data = Data.Date(s) # convert to Date object
                                obj.SetData(prop, data)

        # check altnames
        naltnames = 0
        if checkaltnames:
            print 'checking altnames...'
            for obj in self.rootdict.itervalues():
                altname = getattr(obj,'altname','')
                if not isinstance(altname, str):
                    print 'bad altname'
                    naltnames+=1
                    if fix:
                        obj.altname='foodoo'+str(naltnames)
                        print 'altname changed to '+obj.altname

        # check names
        nnames = 0
        if checknames:
            print 'checking names...'
            for obj in self.rootdict.itervalues():
                name = getattr(obj,'name','')
                if not isinstance(name, str):
                    print 'bad name'
#                    print name
                    print type(name)
                    nnames+=1
                    if fix:
                        obj.name='foofoo'+str(nnames)
                        print 'name changed to '+obj.name
                        

        s = 'Database problems:\n'
        s += '  bad objectids: %d \n' % nids
        s += '  wasteful Data objects: %d \n' % ntypes
        s += '  incorrect date storage: %d \n' % ndates
        s += '  incorrect altnames: %d \n' % naltnames
        s += '  incorrect names: %d \n' % nnames
        if fix: 
            s += 'Fixed.'
        return s


    def __str__(self):
        
        #size = Data.Number(size, 'bytes') # specify units so can spit out '3.2MB' etc
        import os.path
        size = os.path.getsize(self.filename)
#        s = "Abby database file '%s', %d objects." % (self.filename, len(self))
        s = "Abby database file '%s', %d bytes, %d objects." % (self.filename, size, len(self))
#        s = "Abby database file '%s', %s, %d objects." % (self.filename, size, len(self))
        return s



#---------------------------------------------------------------------------


import unittest

class TestAbbyUI(unittest.TestCase):    
    """
    This is the AbbyUI / PythonUI test
    """
    # it's silly to split all these tests up into separate methods - 
    # a real pain, esp with a database...
    
    def testall(self):
        
        # create new db    
        filename = 'test.abby'
        abby = Abby()
        abby.Open(filename, True)
        self.assert_(os.path.exists(filename))
        abby.Add('Type','Type')
        obj = abby.Add('Type','Property')
        obj.altname='prop'
#        abby.Add('Type',
        abby.Add('Property','Id')
        abby.Add('Property','Name')
        obj = abby.Add('Property','Description')
        obj.altname = 'desc'
        abby.Add('Property','Altname')
        abby.Add('Property','CreationDate')
        abby.Add('Property','Value')

        abby.Save()
        abby.Close()
        
        # reopen (existing) file
        abby.Open(filename)

        # add some more
        abby.Add('Type','Subject')
        abby.Add('Type','Equation')
        abby.Add('Subject','Math')
        abby.Add('Equation','Standard Deviation','balewijlij')
        abby.Add('Equation','Law of Cosines','iawjiejlijij')    

        # get a single object
        rs = abby.Get('Standard Deviation')
        self.assert_(len(rs)==1)
        obj = rs[0]
        
        # assign an altname
        obj.altname='stddev'
        abby.Close()
        abby.Open(filename)
        
        # make sure we get the same object
        rs = abby.Get('stddev')
        self.assert_(len(rs)==1)
        obj2 = rs[0]
        self.assertEqual(obj,obj2)
            
        # add an object
        obj = abby.Add('Equation','Normal Distribution')
        obj.equation='1/sqrt(2pi) * exp(-x^2/2)'
        # bomb on re-add
        #, more specific exception catching would be nice...
        self.assertRaises(AbbyError, abby.Add, ('Equation','normal distribution'))
        
        # do a small query 
        rs = abby.Get(type='equation')
        self.assert_(len(rs)==3)

        # test size
        rs = abby.Get(exactname='stddev')
        self.assert_(len(rs)==1)
        obj = rs[0]
        self.assert_(obj.size==28)
    
        # test edit
        rs = abby.Get(exactname='stddev')
        obj=rs[0]
        obj.desc='hahaha'
        abby.Close()
        abby.Open(filename)
        rs = abby.Get(exactname='stddev')
        obj=rs[0]
        self.assert_(obj.desc=='hahaha')

        # keyerror
        self.assertRaises(KeyError, abby.Get, id=99) # doesn't exist

        # close and save file
        abby.Save()
        abby.Close()
        

if __name__ == "__main__":
    unittest.main()

