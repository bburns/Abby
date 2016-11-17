
"""
Layouts module
Layout objects define the physical layout of output to console, files, etc.

Think of it as an abstract form or report class.

layouts:
    Table       report-like format
    Properties  vertical listing of properties
    Card        little business card-like layout
    String      just a plain string output
    Quiz        multiple choice quiz layout
    
"""


#from sets import *
#. layout.append, count, extend, index, insert, pop, remove, sort?

import csv


import Abby # for .Abby assertions
import Data
import Objects


import logging
log = logging.getLogger('')
log.debug('loading layouts.py')


maxcolwidth = 40
screenwidth = 100


import textwrap
wrapper = textwrap.TextWrapper()
wrapper.width = screenwidth
wrapper.replace_whitespace = False



#, for now, just keep list of props you want to hide
# later could modify this through ui
# or let user have various views on data
hiddenprops = ['creationdate'] 



class PropRef:
    """
    This class is used for both tabular (horizontal) and detail (vertical) layouts.
    In the table layout it stores column info.
    In the properties layout it stores row info. 
    """
    def __init__(self, abby, propname, colwidth=None, height=1):
        # get prop object here
        # propname should be external name
        # if prop not found, this will return empty objs list...
        rs = abby.Get(exactname=propname)
        if not rs:
            print propname
            assert rs, "Can't find object named '%s'" % propname
        ## assert len(rs==1)
        self.prop = rs[0]
        self.name = propname
#        self.displayname = Objects.GetExternalName(propname)
        #, downcast to Propdef class?
        # could get default size from property def?
        #. or set to autowidth, with some maximum size
        # could just get align and format from property def
        # store internal name and external name

        #. these will come from propobj.defaultwidth or something
        if colwidth==None:
            
            if propname=='Name':
                colwidth = 30
            elif propname=='Altname':
                colwidth = 12
            elif propname=='Type':
                colwidth = 14
            elif propname=='Description':
                colwidth = 60
                
            #, these are col headers for Properties layout
            elif propname=='Property':
                colwidth = 20
            elif propname=='Value':
                colwidth = 80
                
            # default
            else:
                colwidth = 20
                
        ## if colwidth > maxcolwidth:
            ## colwidth = maxcolwidth
                
        self.width = colwidth
        self.height = height
        self.align = 0
        self.format = '%'
        #self.formatstring = '%' + ('-%ds ' % self.width)   # eg %-30s 
        
        
    def GetFormatString(self):
        return '%' + ('-%ds ' % self.width)   # eg %-30s 
        
    def __str__(self):
#        return self.displayname
        return self.name

    #, getstring (formattype) here?

    def Autosize(self, ob, formattype):
        """
        autosize this column based on the given list of objects
        """
        # first get the column header width
        self.width = len(self.prop.name)
        #colwidths[self.prop.id] = width
        # now walk through rows
        for obj in ob:
            ## for propname in self.propnames:
                ## propvalue = obj.GetValue(propname, formattype)
                ## ncols = len(propvalue)
                ## if ncols > colwidths[propname]:
                    ## colwidths[propname] = ncols
            ## for prop in self.cols:
            data = obj.GetData(self.prop)
#            s = self.prop.Unwrap(data, formattype)
            s = data.GetString(formattype)
            width = len(s)
            if width > self.width:
                self.width = width

        if self.width > maxcolwidth:
            self.width = maxcolwidth


def GetPropNames(propnames):
    """
    Return a modified version of the argument as a list of property names. 
    """
    #, 'all' is dubious here
    if propnames=='default' or propnames=='all': 
        # use for all props to set right order...
#        propnames = ['name','altname','type','description'] # default
        propnames = ['Id','Name','Type','Description'] # default
        
    #, and remove any props that should be hidden
    # works, but also removes them from export!
    #for propname in hiddenprops:
        #if propname in propnames:
            #propnames.remove(propname)
    
    return propnames


def GetPropRefs(abby, propnames): #, colwidths=None):
    """
    Get a list of property objects from the given list of property names.
    propnames should be external names (??)
    ## colwidths is a dictionary of column widths.
    """
    # a List Comprehension:
    # constructs a list of propref objects, referring to property defs
#    list = [PropRef(abby, name) for name in propnames]
    list = []
    ## colwidth = None # default
    for propname in propnames:
        ## if colwidths:
            ## #. put the +4 here for now, but really should separate
            ## # colwidth from textwidth. ie autosize got textwidth, 
            ## # and colwidth includes size of spacer (which depends on Stream used, etc)
            ## colwidth = colwidths[propname] + 4
        ## list.append(PropRef(abby, propname, colwidth))
        list.append(PropRef(abby, propname))
    return list
    


def Factory(abby,layouttype):
    """
    Build a layout object of the given type.
    eg   layout = Layouts.Factory('Table')
    """
    # make string eg "Table(abby, ob)" and evaluate it.
    s = "%s(abby)" % layouttype.capitalize()  
    layout = eval(s)
    return layout
    
    

#------------------------------------------------------------------------------

# base class
class Layout:
## # derive from Data, since 
## class Layout(Data.Data):

    def __repr__(self):
        return 'Layouts.%s(...)' % self.__class__.__name__ # eg Table or Properties

    def __str__(self):
        return self.GetString()

    def GetString(self, formattype='human'):
        """
        Get a string representation of the given objects by iterating
        over the available rows.
        General to all layout classes.
        """
        s = ''
        for srow in self.GetLines(formattype):
            s += srow+'\n'
        return s


    #. could make this the iterator for the layout, so
    # for line in layout:
    #. or GetRows as the iterator, so
    # for row in layout:
    def GetLines(self, formattype='human'):
        """
        Returns an iterator over rows of strings.
        """
        
        ishuman = (formattype=='human')

        #.... delim depends on formattype!
        # could pass stream here instead of formattype,
        # so could get delim and formattype from the stream...?
        # but seems a little funky to pass a stream here...
        delim = ', '
        if ishuman: delim = '  '
            
        nrow = 0
        for row in self.GetRows(formattype):
            s = ''
#            for data, propref in zip(row, self.proprefs):
            for data, col in zip(row, self.cols):
                
                sdata = data.GetString(formattype)
                if ishuman:
                    # Truncate
                    # trim to width of cell also
                    maxwidth = col.width
                    if len(sdata) > maxwidth:
#                        s = s + col.formatstring % (sdata[:maxwidth-3] + '...')
                        s = s + col.GetFormatString() % (sdata[:maxwidth-3] + '...')
                    else:
#                        s += col.formatstring % sdata
                        s += col.GetFormatString() % sdata
                else:
                    # Don't Truncate
                    s += sdata + delim
            if not ishuman: # ie it's a file format like csv
                s = s[:-len(delim)] # remove last delimeter
            yield s
            
            # add line of dashes after header row ----------------
            if ishuman and nrow==0:
                nchars = 0
                for col in self.cols:
                    nchars += col.width
                nchars += len(delim) * (len(self.cols)-1) # add length for gaps
                line = '-'*nchars
                yield line
            nrow += 1



#------------------------------------------------------------------------------


class Properties(Layout):
    
    """
    Properties layout
    """

#    def __init__(self, abby, ob=Objects.Objs(), showprops='all'): # this gave problems
    def __init__(self, abby, ob=None, showprops='all'):
        """
        ob is a list of objects.
        Pass showprops='all' to show all properties used by the objects,
        or pass list of property names. Or pass 'default' to show default props.
        """
        if ob is None:
            ob = Objects.Objs()
        ## assert(isinstance(abby,Abby.Abby))
        ## assert(isinstance(ob, Objects.Ob))
        self.abby = abby
        self.ob = ob
        
        #, same propnames code as in Table...
        self.showallprops = (showprops=='all')
        self.propnames = GetPropNames(showprops)
        
        self.proprefs = GetPropRefs(self.abby, self.propnames)

        colnames = ['Property','Value']
        self.cols = GetPropRefs(self.abby, colnames)


    def GetRows(self, formattype='human'):
        """
        Returns an iterator over rows of lists of property values.
        eg  [Data.String('project'), Data.Date('2004-12-05'), Date.Number(1.23)]
        """

        # Add header row
        row = [Data.Wrap(col.name) for col in self.cols]
        yield row
        
        # Add specified properties
        for propref in self.proprefs:
            data1 = Data.Wrap(propref.name)
            data2 = self.ob.GetData(propref.prop)
            row = [data1, data2]
            yield row

        # Now show all other properties
        if self.showallprops:
            for propname in self.ob.__dict__.iterkeys():
                propname = Objects.GetExternalName(propname)
                if propname not in self.propnames:
                    #print propname
                    #. need some way of handling this nicely...
                    rs = self.abby.Get(exactname=propname)
                    prop = rs[0]
                    assert prop, "No object found with name '%s'" % propname
                    data1 = Data.Wrap(propname)
                    data2 = self.ob.GetData(prop)
                    row = [data1, data2]
                    yield row



class Quiz(Layout):
    """
    Handler for quiz layouts.
    """

    def __init__(self, abby, ob, properties=None):
        self.abby = abby
        self.ob = ob
        if not properties:
            # default: given a name, choose the right description
            ## self.propnameQ = 'Name'
            ## self.propnameA = 'Description'
            self.propQ = abby.Get(exactname='Name')
            self.propA = abby.Get(exactname='Description')
        else:
            ## propQ = properties[0]
            ## propA = properties[1]
            ## self.propnameQ = propQ.name
            ## self.propnameA = propA.name
            self.propQ = properties[0]
            self.propA = properties[1]
    
    
    def GetLines(self, formattype='human'):
        
        ob = self.ob
        if not ob: return # quit if no objects
        obj = ob[0] # first object in list is the question obj
#        objvalue = obj.GetValue(self.propnameQ, formattype)
        data = obj.GetData(self.propQ) #, formattype)
        sdata = data.GetString(formattype)
        s = 'What is %s of %s?' % (self.propA.name, sdata)
        yield s
        
        for i in range(4):
            obj = self.ob[i]
            letter = chr(ord('a') + i)  # a...d
#            sdata = obj.GetValue(self.propnameA, formattype)
            data = obj.GetData(self.propA)
            sdata = data.GetString(formattype)
            s = '  %s. %s' % (letter, sdata)
            yield s



class String(Layout):
    """
    Handler for a simple string message. 
    eg
        layout = Layouts.String('well hello there')
    """
    def __init__(self, s):
        self.s = s
        #, empty object list - since most code expects the layouts to 
        # encapsulate an object list
        self.ob = Objects.Obj() 
    def GetString(self):
        return self.s
    def GetLines(self, formattype='human'):
        yield self.s






class Table(Layout):
    
    """
    Table layout
    """
    
#    def __init__(self, abby, ob=[], showprops='default'):
    def __init__(self, abby, ob=[], groupby=[], sortby=[], showprops='default'):
        """
        ob is a list of objects.
        Pass showprops='all' to show all properties used by the objects,
        or pass list of property names. Or pass 'default' for default properties.
        """
        log.debug('table.init(ob=%s)' % ob)
        self.abby = abby
        self.ob = ob
        self.groupby = groupby
        self.sortby = sortby
        
#        self.autosize = False
        self.autosize = True
#        self.maxwidth = 80 #? ie of each column
        ## self.sortorder = 'type,name' #? or assume ob is already sorted?
        ## self.filter ='hidden is false'

        self.showallprops = (showprops=='all')
        self.propnames = GetPropNames(showprops)
        self.cols = None

    #,
    ## def ApplySort(self):
        ## self.ob.SortBy(self.sortby)

        
    def GetRows(self, formattype='human'):
        """
        Returns an iterator over rows of lists of property values.
        eg  [Data.String('project'), Data.Date('2004-12-05'), Date.Number(1.23)]
        """
        
        ## # If no objects, return a message for the human...
        ## if not self.ob:
            ## if ishuman: yield 'No data' # only for human now
            ## return # this will raise StopIteration

        ## log.debug(self.ob)
        # sort objects first...
        if self.sortby:
            self.ob.sort(lambda x,y:cmp(x.GetSortValue(self.sortby),y.GetSortValue(self.sortby)))
        else:
            #, default sort order... (by type then name)
#            self.ob.sort(lambda x,y:cmp((x.type + x.name).lower(),(y.type + y.name).lower()))
            self.ob.sort(lambda x,y:cmp((str(x.type) + x.name).lower(),(str(y.type) + y.name).lower()))
        ## log.debug(self.ob)

        # Get properties to display and/or column widths
        if self.showallprops or self.autosize:
            # walk through all objects and add any additional properties we don't have yet
            for obj in self.ob:
                ## log.debug(obj)
                if self.showallprops:
                    #objprops = obj.__dict__.keys()
                    #objprops = filter(lambda x: x not in self.propnames, objprops)
                    for propname in obj.__dict__.iterkeys():
                        propname = Objects.GetExternalName(propname) # must use external version
                        if not propname in self.propnames: 
                            self.propnames.append(propname)

        # Get list of PropRef objects for columns
#        self.cols = GetPropRefs(self.abby, self.propnames, colwidths)
        self.cols = GetPropRefs(self.abby, self.propnames)
        
        # Autosize columns
        if self.autosize:
            for col in self.cols:
                col.Autosize(self.ob, formattype)

        # Add column header row
        row = []
        for col in self.cols:
            row.append(Data.String(col.name))
        yield row
        
        # Add objects
#!        print self.ob #!
        for obj in self.ob:
            # build up each row as a list of Data objects
            row = []
            for col in self.cols:
                ## data = obj.GetValue(col.name) # get the Data object
                data = obj.GetData(col.prop) # get the Data object
                row.append(data)
            # done with this row, so yield it back to the caller...
            yield row

        # stop the iterator
        return 



    def Parse(self, stream):
        """
        Iterator that returns command objects that it builds from the tokens 
        returned by the given stream object.
        This is used by Import.
        """
        
        import csv # python library
        
        print 'stream:',stream
        formattype = stream.formattype # eg ascii, human, asciiNoCR
        #, this bombs with "TypeError: argument 1 must be an iterator"
#        reader = csv.reader(stream) 
        reader = csv.reader(stream.file, delimiter=stream.fielddelim)
        # first line should be field names
        # read first row and parse into fields (ie property names)
        #, note: this is different from self.propnames... consolidate somehow...
        propnames = reader.next()
        #, make sure they are lowercase
        # actually, want them to be capitalized
        ## for propname in propnames:
            ## propnames[ = propname.lower()
#        propnames = [propname.lower() for propname in propnames]
#        propnames = [Objects.GetInternalName(propname) for propname in propnames]
        propnames = [Objects.GetExternalName(propname) for propname in propnames]
        print 'propnames:',propnames
        #, get propobjs and proptypes
        props = []
        for propname in propnames:
            #, this is liable to bomb if user gives bad propnames...
            prop = self.abby.Get(exactname=propname)
            props.append(prop)
        
        import Commands
        
        # get rows of property value lists from the stream, one by one
        for row in reader:
            # eg row=['neomem','project',''] 
            print 'row:',row
            # get a dict of propnames and propvalues
            # basically stitch the two lists together...
            ## obj = Objects.Obj()
            ## for propname, propvalue in zip(propnames, row):
                ## obj.SetValue(propname, propvalue)
            ## self.abby._AddToIndex(obj) # this may raise an exception
            #, easier way to do this?
            # build a composite Clause object 
#            clauses = Commands.Clauses()
            setcmds = Data.List() #?
#            for propname, propvalue in zip(propnames, row):
            for prop, propvalue in zip(props, row):
                # save name for later...
#                if propname=='Name':
                if prop.name=='Name':
                    name = propvalue # string value 
                #dict[propname] = propvalue
                # wrap the propvalue string in a Data object
#                data = Data.Wrap(propvalue, formattype)
                #propvalue = Data.Factory(proptype, propvalue, formattype)
#                clause = Commands.Clause(propname, '=', data)
#                clause = Commands.Clause(prop, '=', data)

                #. set commands are not so appropriate here because they require an Object
                # to be applied to - clauses did not!
                setcmd = Commands.Set(obj, prop, propvalue)
                setcmds.append(setcmd)
            # must pass unique name here!
#            cmd = Commands.Add(self.abby, name=name, clauses=clauses)
            cmd = Commands.Add(self.abby, name=name, setcmds=setcmds)
            yield cmd
            
        # stop the ride...
        return




#------------------------------------------------------------------------------

def Test():
    
    
    #. remove abby, just use global namespace
    import Abby
    import Commands
    import Streams
    
    filename = 'test.abby'
    abby = Abby.Abby()
    abby.Open(filename, False)

    print 'Get equations...'
    rs = abby.Get(type='equation')
    print rs
    print
    
    print 'Get same list in human format...'
    layout = Table(abby, rs, showprops='all')
    # this approach works as well...
    ## stream = Streams.Console()
    ## stream.WriteFromLayout(layout)
    s = layout.GetString()  # 'human' is the default here
    print s
    print

    print 'Get same list in ascii format...'
    s = layout.GetString('ascii')
    print s
    print

    print 'Get stddev...'
    rs = abby.Get(exactname='stddev')
    print rs
    print

    print 'Show it...'
    cmd = Commands.Show(abby, rs)
    layout = cmd.Do()
    print layout
    print

    print 'List all (human)...'
    rs = abby.Get()
    layout = Table(abby, rs, 'all')
    # should default to human, ie console, ie spaces as delims
#    file = Streams.Console()
    s = layout.GetString()
    print s
    print
    
    print 'List all (ascii)...'
    s = layout.GetString('ascii')
    print s
    print

    print 'Test factory...'
    layout = Factory(abby, 'table')
    print layout
    print


    abby.Close(False)  # discard all changes
    
    
    # define a layout specific to a particular type (equation)
    ## layoutEquation = Layout('details',['name','description','equation'],
            ## ['type','creationdate','image'])
    ## layoutEquation.GetString(eqn2,'text')
    ## layoutEquation.GetString(eqn3,'ini')

    ## layoutEvents.sortorder='<date,>size'
    ## layoutEvents.filter = "subtype!='later' or 'soon'    "  #?


if __name__=='__main__':
    Test()
    
