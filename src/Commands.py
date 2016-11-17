
"""
Commands 
Defines command classes that are used to interface with Abby database.

Provides for Undo abilities.
All command classes have the same interface.
Also defines the CommandHistory class. 

commands: 
    add
    debug
    delete
    edit
    export
    find
    import
    list
    lookup
    print
    quit
    quiz
    redo
    set
    show
    undo


todo:
split each command out into a file in a Commands folder

"""


"""
The "do" method is expected to store any information needed to "undo" 
the command. For example, the command to delete an item would 
remember the content of the item being deleted. 
Here's where the undo/redo comes in: You have a stack of objects (which 
could be implemented as an array). When you want to execute a command, 
you construct a command object of the appropriate type, call its "do" method. 
If "do" succeeds, you push it to the command stack (append it to the array). 
When you want to undo a command, you call the undo method of the command 
at the stack pointer, and decrement the stack pointer. 
When you want to redo a command, you increment the stack pointer and 
call the "do" method of the object at the stack pointer. 
Note that the act of pushing a new command to the command stack 
truncates the stack at that point, discarding all of the command objects 
after the current top-of-stack stack entry. 
Redoing and undoing just move the stack pointer up and down the stack. 

One of the problems with this pattern is that it can cause an explosion of 
little command classes. It is important to have a good naming convention 
and to do your best to factor common classes. 

Some languages like Lisp and Python have built-in features to pass around 
methods. This can be used instead of this pattern, or as a way to implement it. 
"""

# receiver/target is the abby database object or Obj object

#. define command history class here




import csv  # for export
import os   # for linesep
import random   # for random command


import Data
import Layouts
import Objects
import Streams


import logging
log = logging.getLogger('')
log.debug('loading commands.py')




class CommandUI:
    """
    This class will encapsulate access to the abby object, and stores
    command history.
    """
    def __init__(self, filename):
        self.filename = filename

        import Abby
        self.abby = Abby.Abby()
        self.abby.Open(filename, False)


    def Do(self, cmd):
        """
        Run the given command object, and tie it into the command history
        for undo, etc.
        Returns results of commands, if any, which is usually a Layout object,
        containing the resulting object, and/or result string, etc.
        """
        #, add to history
        layout = cmd.Do()
        return layout
        

    #.
    def Undo(self):
        pass
#        self.it = None # set current object
        
    def Redo(self):
        pass
#        self.it = None # set current object





class Comparisons(list):
    """
    Composite of several Comparison objects. 
    Can be used as a filter. 
    Stores list of property names and values.
    Generates a complete filter string and a filter function.
    """
    def __init__(self, *args):
        list.__init__(self, args) # extended list (works)


    def GetFilterFunction(self):
        """
        Returns a filter function that can be applied to an obj with result T or F.
        eg    lambda obj: obj.project=='abby' and obj.type=='todo'
        """        
        s = "lambda obj: " + str(self)
        fn = eval(s)
        log.debug('created filter function: %s' % s)
        return fn
        

    ## def ApplyToObj(self, obj):
        ## """
        ## apply this collection of comparisons to the given object.
        ## ie assuming the comparisons are assignment statements.
        ## """
        ## for comparison in self:
            ## comparison.ApplyToObj(obj)
            
    def __str__(self):
        """
        Build a filter string from this list of comparisons. 
        Will be used in defining a lambda function for searching through the database.
        """
        s = 'True'
        for comparison in self:
            s += " and %s " % str(comparison)
        return s

    def SetOperator(self, operator):
        for comparison in self:
            comparison.operator = operator



class Comparison:
    """
#    single comparison (prop, operator, data)
    single comparison (prop, operator, propvalue)
    """
    def __init__(self, prop, operator, propvalue):
        """
        prop can be propobj, propname or None.
        if None then data is an adjective, eg 'hw'
        propvalue can be string or Ob or Data object?
        """
        log.debug('create Comparison(%s,%s,%s)'%(prop,operator,propvalue))
        ## data = Data.Wrap(propvalue)
        
        if prop==None: # was 'self'
            # we must just have an object for the property value, 
            # so use the object's type for the propname.
            adj = propvalue
            assert(isinstance(adj,Objects.Ob))
            #propname = str(adj.type).lower()  # eg 'project'
            prop = str(adj.type).lower()  # eg 'project'
            #, for now just use obj name. in future, cf by id?
            propvalue = adj.name.lower()
        ## elif isinstance(prop, Objects.Ob):
            ## propname = prop.name
            ## #, get proptype here
            ## # proptype = prop.GetValue('propertytype')
        ## else:
            ## propname = prop
            
#        self.propname = propname
        self.prop = prop
        self.operator = operator
        self.propvalue = propvalue
        
    
    ## def ApplyToObj(self, obj):
        ## """
        ## apply this collection of comparisons to the given object.
        ## ie assuming the comparisons are assignment statements.
        ## """
        ## assert(self.operator=='=') # make sure this is an assignment
        ## log.debug('comparison.applytoobj: %s=%s' % (self.prop, self.data))
        ## obj.SetData(self.prop, self.data)

    def SetOperator(self, operator):
        self.operator = operator


    def __str__(self):
        """
        Build a comparison string for this comparison.
        """
        #, for now do string comparison for everything. in future, Data obj comparison??
#        s = "obj.GetValue('%s').lower()%s'%s'" % (self.propname, self.operator, self.propvalue)
#        s = "obj.GetData(%s)%s%s" % (self.prop, self.operator, self.data)
        s = "obj.GetValue('%s').lower()%s'%s'" % (self.prop, self.operator, self.propvalue)
        return s

    def __getitem__(self, key):
        if key==0:
            return self
        raise IndexError        
    def __iter__(self):
        yield self # return this object
        raise StopIteration # that's all folks
    def __len__(self):
        return 1



#----------------------------------------------------------------------------


# base class
"""
this should derive from Obj, since commands will have name, type, desc, so can do:
> list commands
> help add
> add pphys hw 'read ch1', due fri
(how would this know it's not an implicit add of something with .action=add???
eg
> add feature 'neomem forum' (could be .action=add)
ah well, ambiguity, deal with it. 
for now, if first word is add, treat it as the command.
)
"""
#class Command:
#class Command(Data.Data):
class Command(Objects.Obj):
    
    def __init__(self, abby=None):
        self.abby = abby
        
    def Do(self):
        # should always return a layout object
        return Layouts.String('(did nothing)')
    
    def Undo(self):
        pass
    
    def __repr__(self):
        return 'Commands.%s(...)' % self.__class__.__name__ # eg List or Set

    def __str__(self):
        return 'empty command object (or undefined __str__?)'
#        return self.commandname
        


#----------------------------------------------------------------------------

## #, just use List? or derive from List?
## class Commands(Command):
    ## """
    ## Aggregate commands.
    ## """
    ## def __init__(self):
        ## pass
        

#------------------------------------------------------------------------------

class Add(Command):

    #. grammar and code will be used in building the parser (semidynamically) 
    #, parser will give you variables as directed in .grammar,
    #, could expect 'data' in return? or code as an actual method?
    name = "Add"
    type = "Command"
    description = "Add a new object to the main namespace."
    example = "add pphys hw 'read ch1,2' due friday, rating ***"
    grammar = "ADD [adjectives] [type] name [description] [assignment_clauses]"
    code = "data = Commands.Add(abby, type, name, description, adjectives)"
    #, actually, code could be an actual method, not just a string!? eg
    ## def ParserCode(adjectives, type, name, description, assignments):
        ## cmd = Add(adjectives, type, name, description, assignments)
        ## return cmd
        
    ## def __init__(self, abby, type='',name='',description='',altname='', 
                    ## adjectives=[], dict=None, clauses=[]):
#    def __init__(self, abby, type='', name='', description='', altname='', clauses=[]):
#    def __init__(self, abby, type='', name='', description='', adjectives=Objects.Objs()):
    def __init__(self, abby, type='', name='', description='', adjectives=None): #, assignments=Sets()):
        """
        eg cmd = Commands.Add(abby, 'fish', 'plecostomus', 'cool looking fish')
        """
        assert(isinstance(name,str))
        assert(isinstance(type,str))
        ## assert(isinstance(description,str)) #, might be None (from parser)
        self.abby = abby
        self.type = type
        self.name = name
        self.description = description
        self.adjectives = adjectives # ob
#        self.dict = dict  # dict of property names and values to add
#        assert(isinstance(adjectives,Objects.Ob))
#        self.assignments = assignments
        
    def Do(self):
        
        # this can throw an exception - let caller handle it.
        obj = self.abby.Add(self.type,self.name,self.description) #,self.altname)

        # set any adjectives
        # bug: had a loop here using obj as loop variable also, clobbering the original obj!!
        obj.PutIn(self.adjectives)

        # set any other property values defined in the assignments object
#        self.assignments.ApplyToObj(obj)

        # save state for undo
        self.id = obj.id

        # set abby.it
        self.abby.it = obj

        #, resolve this (string vs view of object...)
        if len(obj.name) > 30:
            name = obj.name[:30]+'...'
        else:
            name = obj.name
        s = "Added %s '%s'." % (obj.type, name)
        return Layouts.String(s)
        ## layout = Layouts.Properties(self.abby, obj)
        ## return layout
        


    def Undo(self):
        # delete the object that was added (ie remove it from the main index)
        self.abby.Delete(self.id)

    def __str__(self):
        s = "Add Object '%s'" % self.name
        return s



#----------------------------------------------------------------------------
class Debug(Command):
    def __init__(self, abby, debug):
        self.abby = abby
        self.debug = debug
    def Do(self):
        self.abby.SetDebug(self.debug)
        ## self.abby.debug = not self.abby.debug
        s = "Debug set to %s" % self.debug
        return Layouts.String(s)
    def __str__(self):
        s = "Debug %s" % self.debug
        return s
        
#----------------------------------------------------------------------------


class Delete(Command):
    
    name = "Delete"
    altname = "del"
    type = "Command"
    description = "Delete an object from the main namespace, or delete a property from an object."
    example = "delete lotr  |   delete lotr.desc"
    grammar = "DELETE [reference]"
    code = "cmd = Commands.Delete(reference)"
    
    #, allow deleting multiple objects?
    #, really should move to a trash can so can recycle
    
    def __init__(self, abby, ob):
        self.abby = abby
        self.ob = ob
        self.name = str(ob) #self.ob.GetValue('name')
        
    def Do(self):
        self.abby.Delete(self.ob)
        s = "Deleted '%s'." % self.name
        return Layouts.String(s)
        
    def Undo(self):
        # need to get into the Abby mechanism here, hence the _AddToIndex
        #, handle ob!
        self.abby.__AddToIndex(self.ob)
        
    def __str__(self):
        s = "Delete '%s'" % self.name
        return s
        
        
        
#----------------------------------------------------------------------------

class Edit(Command):
    
    name = "Edit"
    type = "Command"
    description = "Edit the specified object or attribute (object.property) in a window (Notepad for now)."
    example = "edit abby"
    grammar = "EDIT reference"
    code = "cmd = Commands.Edit(reference)"

    #, allow attributes
    #, for now, just edit the description property in notepad.
    
    def __init__(self, abby, obj):
        
        #, kludge: parser is returning Objs for a single object...
        if isinstance(obj, Objects.Objs):
            obj = obj[0]
        assert(isinstance(obj, Objects.Obj))
        
        self.abby = abby
        self.obj = obj
        self.name = str(self.obj)
        
    def Do(self):
#        filename = '__tempedit.txt'
        newname = self.name[:20].replace(' ','_')
        newname = newname.replace('/','_')
        filename = '__' + newname + '_description.txt'
        # get description
        s = self.obj.GetValue('description') 
        # save it to a temp file
        open(filename,'w').write(s)
        # edit file in notepad
        command = "notepad.exe %s" % filename
        pipe = os.popen(command)
        nada = pipe.read() # pipe will return '' when notepad closes
        # load file
        snew = open(filename,'r').read()
        # if description changed, save to the object
        ischanged = s != snew
        if ischanged:
            self.obj.SetValue('description', snew) # save new description
            status = "Object '%s' edited." % self.name
        else:
            status = "No changes made to object '%s'." % self.name
        # make sure to delete the temporary file also
        os.remove(filename)
        # set current object
        self.abby.it = self.obj 
        # return status message
        layout = Layouts.String(status)
        return layout

    def __str__(self):
        s = "Edit '%s'" % self.name
        return s


#----------------------------------------------------------------------------

class Expression(Command):
    """
    """
    def __init__(self, abby, ref):
        self.abby = abby
        self.ref = ref
    def Do(self):
        pass
    def __str__(self):
        s = "Expression..."
        return s
        
        
#----------------------------------------------------------------------------

class Export(Command):

    name = "Export"
    type = "Command"
    description = "Export the specified objects to a file."
    example = "export words to words.csv"
    grammar = "EXPORT [adjectives] [TO] filename"
    code = "cmd = Commands.Export(adjectives, filename)"
    
    def __init__(self, abby, filename, streamtype=None, adjectives=None):
        """
        UI (gui or abby...) is responsible for giving this routine a filename!
        ie get from dialog or whatever...
        Can override streamtype here - default is based on file extension.
        """
        self.abby = abby
        self.filename = filename
        self.streamtype = streamtype
        self.adjectives = adjectives # ob
        
        
    def Do(self):
        
        # Build the export file and wrap it in a stream object
        # bug: forgot self in filename in similar case - wound up overwriting stuff.abby file by passing None!!!!!
        # bug: must write in binary mode or screws up endline!!
        stream = Streams.Factory(self.filename, 'wb', self.streamtype)
        
        # Build a list command to get the objects to export
        # export all properties!
        cmd = List(self.abby, self.adjectives, showprops='all') #, groupby, sortby)
        layout = cmd.Do() # don't tie into history
        
        # Pass the layout object to the stream object, which will pull 
        # the information from the layout and write it to the file in the
        # proper format.
        stream.WriteFromLayout(layout)

        #, i think the list command will set this via abby.get!
#        self.abby.it = layout.ob #, set current object(s)

        # wrap the status string in a simple String layout object
        nobjects = len(layout.ob)
        s = "%d objects exported to file '%s'." % (nobjects, self.filename)
#        self.abby.status = s #, standardize this
        return Layouts.String(s)


    def __str__(self):
        s = "Export %s to %s" % (self.adjectives, self.filename)
        return s


#----------------------------------------------------------------------------

class Find(Command):

    name = "Find"
    altname = "search"
    type = "Command"
    description = "Find occurrences of the given string in the main namespace."
    example = "find ff"
    grammar = "FIND string"
    code = "cmd = Commands.Find(string)"
    
    def __init__(self, abby, s):
        self.abby = abby
        self.s = s
    def Do(self):
        pass
        #ob = abby.Find(s)
        
    def __str__(self):
        s = "Find %s" % self.s
        return s
        
#----------------------------------------------------------------------------

class Import(Command):
    
    name = "Import"
    type = "Command"
    description = "Import objects from a file into the main namespace."
    example = "import words from 'test.txt'"
    grammar = "IMPORT [adjectives] [FROM] filename"
    code = "cmd = Commands.Import(adjectives, filename)"
    
    def __init__(self, abby, filename, streamtype=None):
        self.abby = abby
        self.filename = filename
        self.streamtype = streamtype

    def Do(self):

        import Abby  # for exception

        # Build the import file and wrap it in a stream object
        ## print 'streamtype:',self.streamtype
        # may throw exception if file not found
        stream = Streams.Factory(self.filename, 'r', self.streamtype) 
        layout = Layouts.Factory(self.abby, stream.layouttype)
        
        ## print 'stream:',stream
        ## print 'layout:',layout
        
        #stream.ReadToLayout()
        
        # the stream will return tokens one by one from the file, 
        # and layout will parse the tokens into commands.
        
        # get a composite command object
        ## cmd = layout.ParseFrom(stream)
        ## layoutresult = cmd.Do()
        
        # more efficient to do this way, so don't get a huge honkin composite cmd!
        ob = Objects.Objs()
        errors = []
        try:
            for cmd in layout.Parse(stream):
                try:
                    # cmd will usually be an Add command
                    layout = cmd.Do()
                    #, build up a list of all the objects added so can report to user
                    ob.append(layout.ob)
                except Abby.AbbyError, e:
                    #. add error to a file also?
                    errors.append(str(e))
        except Exception, e: #, Parser.ParserError, e:
            #errors.append(e)
            #errors.append(str(e))
            raise # pass it on
            
        nobjs = len(ob)
        nerrors = len(errors)
        self.abby.it = ob #, set current object(s)
        s = "%d objects imported from file '%s' [%d errors]." % (nobjs, self.filename, nerrors)
        if errors:
            s = s + '\nErrors:\n\t' + '\n\t'.join(errors)
        return Layouts.String(s)


    def __str__(self):
        s = "Import from '%s'" % self.filename
        return s

#----------------------------------------------------------------------------

#. this would become a query object
# call it Query?
# add filter, sort, grouping, etc
# no undo for this
class List(Command):
    
    name = "List"
    type = "Command"
    description = "List objects in the main namespace that match the given criteria."
    examples = "list books show name, author"
    grammar = "LIST [adjectives] [comparisons] [sortby] [groupby] [SHOW properties]"
    code = "cmd = Commands.List(adjectives, comparisons, sortby, groupby, properties)"
    
    def __init__(self, abby, adjectives=None, comparisons=None, groupby=[], sortby=[], showprops='default'):
        """
        clauses can be composite, eg type==hw and class==neuro.
        pass showprops='all' to show all properties in the objects found.
        """
        self.abby = abby
        self.adjectives = adjectives # ob
        self.comparisons = comparisons
        self.groupby = groupby # ditto
        self.sortby = sortby # ditto
        self.showprops = showprops
        #. best to do any compilation here, so can rerun command faster...
        #. do depluralization here?
        
        # Build a filter for the list, using adjectives and comparisons put
        # into Comparison objects.
        #. filter should be matching object id's!!
#        self.filter = Filter(abby, adjectives)
#        print 'List.clauses="%s"' % self.clauses
        # if adjectives is empty list, then so will list be
#        list = [Comparison('self','==',obj) for obj in adjectives]
        list = []
        if adjectives:
            for obj in adjectives:
                list.append(Comparison(None,'==',obj))
        filter = Comparisons()
        filter.extend(list)
        # add comparisons also (eg "with date")
        if comparisons:
            log.debug('comparisons=%s' % comparisons)
            filter.extend(comparisons)
        self.filter = filter
        log.debug('filter=%s' % filter)
        
    def Do(self):
        rs = self.abby.Get(afilter = self.filter)
        log.debug('cmd list.do -> ob=%s' % `rs`)
        #, let the layout sort the list (since user might change this interactively)?
        # set abby.it
        self.abby.it = rs
        # let ui handle printing the objects...
        layout = Layouts.Table(self.abby, rs, self.groupby, self.sortby, self.showprops)
        return layout

    def Undo(self):
        pass
        
    def __str__(self):
        s = "List %s groupby %s sortby %s" % (self.filter, self.groupby, self.sortby)
        return s



#----------------------------------------------------------------------------

class Lookup(Command):
    """
    Lookup the name of an object in google.
    """
    
    def __init__(self, abby, obj):
        
        #, kludge: parser is returning Objs for a single object...
        if isinstance(obj, Objects.Objs):
            obj = obj[0]
        assert(isinstance(obj, Objects.Obj))
        
        self.abby = abby
        self.obj = obj
        self.name = str(self.obj)
        
    def Do(self):

        # build command to start browser...
        #. use popen to hide cmd console
        url = "http://www.google.com/search?q=dictionary+etymology+" + self.name
        browser = r'C:\Program Files\Mozilla Firefox\firefox.exe'
        cmd = ''' "%s" %s '''  % (firefox, url)
        log.debug(cmd)
        os.system(cmd)

        # return status message
        status = "Looked up '%s' in Google" % self.name
        layout = Layouts.String(status)
        return layout

    def __str__(self):
        s = "Lookup '%s'" % self.name
        return s

#----------------------------------------------------------------------------

class Put(Command):

    name = "Put"
    type = "Command"
    description = "Put object(s) in the given adjectives."
    example = """
        'put alarmclock in kalispell' is like saying 'alarmclock.company=kalispell'
        """
    grammar = "PUT object IN adjectives"
    code = "cmd = Commands.Put(object, adjectives)"

    def __init__(self, abby, ob, adjectives):
        self.abby = abby
        self.ob = ob
        self.adjectives = adjectives # ob
    
    def Do(self):
        # put the objects in the given adjectives
        # eg 'put alarmclock in kalispell' is equivalent to 'alarmclock.company = kalispell'
        for obj in self.ob:
            obj.PutIn(self.adjectives)
        
        # set abby.it
        self.abby.it = self.ob
        s = 'Put %s in %s' % (self.ob, self.adjectives)
        layout = Layouts.String(s)
        return layout        
        
    def Undo(self):
        pass
        
    def __str__(self):
        s = "Put %s in %s" % (self.ob, self.adjectives)
        return s
    



#----------------------------------------------------------------------------


#?
class Quit(Command):
    def __init__(self):
        pass
    def Do(self):
        #. ask if should save changes...
        #raise 
        pass
        
#----------------------------------------------------------------------------

class Quiz(Command):
    
    name = "Quiz"
    type = "Command"
    description = "Ask user the definition of a random object (multiple choice)."
    examples = """
        quiz words
        quiz physics terms
        quiz music terms
        quiz 'amino acids' show name ask code
        quiz 'amino acids' show symbol ask name
        quiz 'amino acids' show structure ask symbol
        """
    productions = """
        showprop : SHOW property
        askprop : ASK property
        """
    grammar = "QUIZ [adjectives] [showprop] [askprop]"
    code = "cmd = Commands.Quiz(adjectives, question, answer)"
    
    def __init__(self, abby, adjectives, properties=None): #propQ='name', propA='desc'):
        self.abby = abby
        self.adjectives = adjectives # ob
        self.properties = properties
        ## self.propQ = propQ
        ## self.propA = propA
        
    def Do(self):
        #. pick 4 rnd objects
        # display def of 0, let user pick object,
        # or display name, let user pick def
        n = 4
        cmd = Random(self.abby, self.adjectives, n)
        layout = cmd.Do()
        
#        obj = layout.ob[0]
#        return layout

        # want to define a new layout to present data in quiz format...
        ob = layout.ob
        newlayout = Layouts.Quiz(self.abby, ob, self.properties)
        
        return newlayout

    def __str__(self):
        return 'Quiz %s' % self.adjectives


#----------------------------------------------------------------------------

class Random(Command):
    
    name = "Random"
    type = "Command"
    description = "Show a random object."
    examples = """
        random quote
        random word
        random compound
        random type
        random
        """
    grammar = "RANDOM [adjectives]"
    code = "cmd = Commands.Random(adjectives)"
    
    def __init__(self, abby, adjectives, n=1):
        self.abby = abby
        self.adjectives = adjectives
        self.n = n # number of objects to get
        
    def Do(self):
        # get a random obj matching given adjectives
                
        # get a list of all objects matching adjectives
        cmd = List(self.abby, self.adjectives)
        layout = cmd.Do()
        oball = layout.ob
        if oball:
            ## print 'possibilities:',oball
            ob = Objects.Objs() # start with empty list
            for i in range(self.n):
                # now choose one of them at random
                #. we'll want to weight this according to 'popularity'
                # which will take various things into account, including
                # last accessed time, number of times accessed, duration of access,
                # number of times right (er, tied in through other db?),
                # uh...
                obj = random.choice(oball)
                ob.append(obj) # add to our list of objects
                
            self.abby.it = ob
            
            if self.n==1:
                layout = Layouts.Properties(self.abby, ob)
            else:
                layout = Layouts.Table(self.abby, ob)
                
        return layout
        
        
    def __str__(self):
        return 'Random %s' % self.adjectives
    

#----------------------------------------------------------------------------

class Save(Command):
    
    name = "Save"
    type = "Command"
    description = "Save the current namespace to a file."
    examples = """
        save
        """
    grammar = "SAVE [filename]"
    code = "cmd = Commands.Save(filename)"
    
    
    def __init__(self, abby, asfilename=''):
        self.abby = abby
        self.asfilename = asfilename #,

        
    def Do(self):
        self.abby.Save()
        s = "%d objects saved to file '%s'." % (len(self.abby), self.abby.filename)
        return Layouts.String(s)


        
        
#----------------------------------------------------------------------------

class Set(Command):
    
    name = "Set"
    type = "Command"
    description = "Set an attribute (object.property) to the specified value."
    examples = """
        set lotr.desc to 'yeah frodo and sam go to mordor'
        lotr.desc = 'woohoo'
        it
        .author = 'tolkein'
        """
    grammar = """
        SET attributeref TO value
        | attributeref EQUALS value
        """
    code = "cmd = Commands.Set(attributeref, value)"
    
    
#    def __init__(self, abby, ob, prop, propvalue):
    def __init__(self, abby, attrib, propvalue):
#    def __init__(self, abby, attrib, data):
        """
        attrib = Attribute object with obj and prop
        prop is a property object ie an obj
        propvalue can be a Data object, an Ob, a string, etc.
        """

        #. use GetData etc
        #, handle for Objs also!

        # get Attribute information
        ob = attrib.obj
        prop = attrib.prop
        data = Data.Wrap(propvalue)
        
        
        # for now assert just one object
        assert(len(ob)==1)
        assert(isinstance(ob, Objects.Ob))
        #, kludge: parser is returning Objs for a single object...
        if isinstance(prop, Objects.Objs):
            prop = prop[0]
        assert(isinstance(prop, Objects.Obj))
        
        self.abby = abby
        self.ob = ob  # list of objects to modify (usually one)
        self.prop = prop
#        self.propvalue = propvalue  # string, obj, date, number, etc.
        self.data = data  # string, obj, date, number, etc.
        
        ## #. er, yuck!!! definitely should use the obj reference if we have it!
        ## self.obname = ob.GetValue('name')
        ## self.propname = prop.GetValue('name')

        #. handle multiple object values here...
        # ie instead of returning 'Multiple values', could return tuple of all values!?
        #. parser should really be giving us an Objs list, not a plain python list!
#        self.oldvalue = ob.GetValue(propname)
        obj = self.ob[0]
#        self.oldvalue = obj.GetValue(self.propname)
        self.olddata = obj.GetData(prop)
        
        
    def Do(self):

        #, modify the objects in the list
#        self.ob.SetValue(self.propname, self.propvalue)

        # for now assert just one object
        assert(len(self.ob)==1)
        obj = self.ob[0]
#        obj.SetValue(self.propname, self.propvalue)
        obj.SetData(self.prop, self.data)
        
        s = "Set %s.%s to %s" % (obj, self.prop, self.data)
        self.abby.status = s #, update abby status
        self.abby.it = obj
        log.debug('set abby.it to %s' % obj)
        return Layouts.String(s)
        
        
    def Undo(self):
        #. handle multiple object values here...
#        self.ob.SetValue(self.propname, self.oldvalue)
        self.ob.SetData(self.prop, self.olddata)
        #, update status
        
    def __str__(self):
#        s = "Set %s.%s to '%s'" % (self.obname, self.propname, self.propvalue)
        s = "Set %s.%s to %s" % (self.ob, self.prop, self.data)
        return s



#----------------------------------------------------------------------------

class Shell(Command):
    """
    Execute a shell command
    """

    def __init__(self, s):
        self.s = s

    def Do(self):
        # open a pipe to the shell command
        # the pipe is like a file object, which you read
        pipe = os.popen(self.s)
        s = pipe.read()
        return Layouts.String(s)



#----------------------------------------------------------------------------

class Show(Command):
    
    name = "Show"
    type = "Command"
    description = "Show the value of a reference (to an object or attribute)."
    examples = """
        show lotr
        show lotr.desc
        lotr
        neuromancer.author
        """
    grammar = """
        SHOW reference
        | reference
        """
    code = "cmd = Commands.Show(reference)"
    
    
    def __init__(self, abby, ref):
        self.abby = abby
        self.ref = ref
        
    def Do(self):
        ref = self.ref
        
        # store reference's object as abby.it
        ob = ref.GetObject()
        log.debug('setting abby.it to %s' % ob)
        self.abby.it = ob
        
        # return a layout object containing the text to display
        layout = ref.GetLayout(self.abby, showprops='all')        
        return layout
        
    def __str__(self):
#        s = "(Show) %s" % self.ref.GetValue('name')
        s = "(Show) %s" % self.ref
        return s

#----------------------------------------------------------------------------

class Verify(Command):
    """
    verify db integrity, correct any errors.
    """
    def __init__(self, abby):
        self.abby = abby
        
    def Do(self):
        s = self.abby.Verify()
        return Layouts.String(s)


#----------------------------------------------------------------------------

#?
## class Undo(Command):
    ## def Do(self):
        ## self.abby.Undo()

## class Redo(Command):
    ## def Do(self):
        ## self.abby.Redo()
## class Load(Command):
    ## def Do(self):
        ## # load another database?
        ## self.abby.Load(filename)

## class Close(Command):
    ## pass

## class Help(Command):
    ## pass



#----------------------------------------------------------------------------


def Test():
    
    import Abby
    filename = 'stuff.abby'
    abby = Abby.Abby()
    abby.Open(filename, False)
    
    
    # so the CommandUI should wrap the AbbyUI, ie we will only deal with a 
    # CommandUI object?
    
    cmdui = CommandUI(filename)
    
    
    rs = cmdui.Get(type='equation')
    print rs
    
    
    
    ## do some changes (not tests)
    ## bug: these changes weren't being saved to the db because Obj wasn't inheriting from Persistent!
    ## warning: can't just say obj.type='Metatype' because zodb doesn't get the message that obj changed?
    #obj = abby.Get(exactname='type') 
##    obj.SetValue('type','Metatype')
    #obj.SetValue('type','Type')
    #print 'obj:',obj
    #print Layouts.Properties(abby,obj)
    #print
    #abby.Close()  # save all changes

    
    #obj = abby.Get(exactname='glutamine')
    #obj.SetValue('symbol','Que')
    #print Layouts.Properties(abby, obj)
    #abby.Save()
    
    
    ## print 'Test List...'
    ## obj = abby.Get(exactname='Project')
    ## cmd = List(abby, obj)
    ## print cmd
    ## layout = cmd.Do()
    ## print layout.ob
    ## print
    
    print 'Test Random...'
    obj = abby.Get(exactname='Type')
    cmd = Random(abby, obj)
    print cmd
    layout = cmd.Do()
    print layout.ob
    print

    print 'Test Quiz...'
    obj = abby.Get(exactname='aa')
    cmd = Quiz(abby, obj)
    print cmd
    layout = cmd.Do()
    print layout.ob
    print layout
    print

    ## print 'Test Add...'
    ## cmd = Add(abby, 'fish', 'pez', 'this is some description')
    ## r = cmd.Do()
    ## obj = r.ob
    ## print r
    ## print


    ## if 0:
        ## print 'add an object using commands'
        ## cmd = Commands.Add(abby, 'Equation','Chi-Square Distribution')
        ## obj = cmd.Do()
        
        ## cmd = Commands.Edit(obj, 'equation', 'f(x)=1/Gamma(r/2)/2^r/2 * x^(4/2-1) * exp(-x/2)')
        ## cmd.Do()
        ## print obj
        ## print
        
    ## if 0:
        ## print 'add object and then undo!'
        ## cmd = Commands.Add(abby, '','testundo!')
        ## obj = cmd.Do()
        ## print obj
        ## print 'undo...'
        ## cmd.Undo()
        ## print obj
        ## print
        
    ## if 0:
        ## print 'add object and then delete then undo!'
        ## cmd = Commands.Add(abby, '', 'testdelete7!')
        ## obj = cmd.Do()
        ## print obj
        ## print 'delete...'
        ## cmd = Commands.Delete(abby, obj)
        ## cmd.Do()
        ## print 'undo...'
        ## cmd.Undo()
        ## print


    ## if 0:
        ## print 'edit an object using commands...'
        ## obj = abby.Get('abulia')
        ## print obj
        ## print 'edit...'
        ## #. bombs - handle obj not having prop
        ## cmd = Commands.Edit(obj, 'equation', 'blargh!')
        ## cmd.Do()
        ## print obj
        ## print 'undo...'
        ## cmd.Undo()
        ## obj = abby.Get('abulia')
        ## print obj
        ## print


    ## print 'Test Set...'
    ## prop = abby.Get(exactname='name') # get name property
    ## propvalue = 'pez'
    ## cmd = Set(abby, obj, prop, propvalue)
    ## print cmd.Do()
    ## ob = abby.Get(type='fish')
    ## print 'ob:',ob
    ## print Layouts.Table(abby, ob)
    ## print
    
    ## print 'Test Edit...'  # calls up Notepad
    ## cmd = Edit(abby, obj)
    ## print cmd.Do()
    ## obj = abby.Get(exactname='pez')
    ## print 'obj:'
    ## print Layouts.Properties(abby, obj)
    ## print
    
    ## print 'Test Delete...'
    ## cmd = Delete(abby, obj)
    ## print cmd.Do()
    ## obj = abby.Get(exactname='pez')
    ## print 'obj:',obj
    ## print
    
    ## print 'Test Set...'
    ## cmd = Set(abby, obj, 'rating','****')
    ## print cmd
    ## layout = cmd.Do()
    ## print 'result:',layout
    ## print
    
    ## #print 'Test Export csv...'
    ## filename = 'testexportcsv.txt'
    ## #cmd = Export(abby, filename, adjectives=obj)
    ## #print cmd
    ## #layout = cmd.Do()
    ## #print layout
    ## #print
    
    ## print 'Big Import csv...' # warning - big file
    ## cmd = Import(abby, 'exportcsv.txt')
    ## print cmd
    ## layout = cmd.Do()
    ## print layout
    ## print
    
    ## print 'Test Export tab...'
    ## filename = 'exporttab.txt'
    ## cmd = Export(abby, filename, streamtype='Tab')
    ## print cmd
    ## layout = cmd.Do()
    ## print layout
    ## print
    
    ## print 'Test Import...'
    ## #filename = 'testin.txt'
    ## cmd = Import(abby, filename)
    ## print cmd
    ## print
    ## print 'file:'
    ## print open(filename,'r').read()
    ## print
    ## # do the import
    ## layout = cmd.Do()
    ## print 'imported:',layout
    ## print
    ## print 'Verify import...'
    ## obj = abby.Get(exactname='4d moon flyer')
    ## print Layouts.Properties(abby, obj)
    ## #cmd = List(abby, obj)
    ## #print cmd
    ## #layout = cmd.Do()
    ## #print layout.ob
    ## print

    abby.Close(False)  # discard all changes
    


#----------------------------------------------------------------------------

if __name__=='__main__':
    
    #. running this module could build the parser code
    # ie go through and extract all command grammars, verb words, etc
    # export token class and parser class to file(s)
    # then run those to build the parser
    # then test the parser by running the parser module?
    
    ## cmd = Save()
    ## print cmd
    
    # Test should be in its own namespace, not in global, because
    # otherwise some errors can slip by, eg referencing abby instead of self.abby!!
    Test()

    
    
