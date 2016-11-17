
"""
Streams
These classes act as go-betweens between Abby data and a stream (a file or stdio).

"""

#. each filetype should get a class that defines file extensions,
# delimeters, view class to use, description, format class to use, etc
# factory will use this info (via introspection) to build correct class


#import types 
import os 


import logging
log = logging.getLogger('')
log.debug('loading streams.py')


def GetStreamType(filename):
    """
    Get the streamtype associated with the given filename.
    """

    # get file extension
    filetitle, ext = os.path.splitext(filename)
    ext = ext[1:] # remove leading period
#    print filetitle, ext

    # map extensions to streamtypes
    streamtypes = {
            'csv' : 'Csv',
            'txt' : 'Csv',
            'htm' : 'Html',
            'html' : 'Html',
            'xml' : 'Xml',
            'ini' : 'Ini',
            'cfg' : 'Ini',
            'b' : 'Binary',
            'ged' : 'Gedcom',
            'console' : 'Console',
            'abby' : 'Abby'
            }
            
    # allow any extension the user wants
    if streamtypes.has_key(ext):
        streamtype = streamtypes[ext]
    else:
        streamtype = 'Csv'
        
    return streamtype



def Factory(filename, openflags='r', streamtype=None):
    """
    Given a filename, return a Stream object of the correct type,
    encapsulating an open file object with that name.
    Can pass a streamtype to override the default, which is normally 
    chosen based on the extension of the given filename.
    """
    #. use introspection to find correct stream class...
    #, on 'r', could check file contents to determine what type of stream to use!

    # Get formattype based on filename, 
    if streamtype==None:
        streamtype = GetStreamType(filename)  # eg Csv, Console
    classdef = eval(streamtype)  # eg class Csv
    formattype = classdef.__dict__['formattype']
    
    s = "%s('%s','%s')" % (streamtype, filename, openflags)
    ## print 'streamtype:',streamtype
    ## print 'formattype:',formattype
    ## print 'eval string:',s
    # may throw exception
    stream = eval(s)   # eg   stream = Csv('test.csv','r')
    ## print 'stream:',stream
    
    return stream



#--------------------------------------------------------------------------

# base class
class Stream:
    
    def __init__(self, filename, openflags='r'):
        """
        This base class init is usually used by the child classes.
        """
        self.filename = filename
        self.openflags = openflags
        self.file = open(filename, openflags) # may throw exception
#        self.streamtype = self.__class__.__name__ # eg Csv or Tab
        
    def __repr__(self):
        # eg Streams.Csv('test.csv', 'r')
        #, get streamtype from introspect
#        return "Streams.%s('%s', '%s')" % (self.streamtype, self.filename, self.openflags)
        return "Streams.%s('%s', '%s')" % (self.__class__.__name__, self.filename, self.openflags)
#        return "Streams.%s('%s', '%s')" % (streamtype, self.filename, self.openflags)

    def writeline(self, s):
        self.file.write(s+'\n')
        


#--------------------------------------------------------------------------

class Console(Stream):
    """
    wraps stdio
    """
    extensions = ''
    formattype = 'human'
#    layouttype = 'Table'
#    fielddelim = ''
    filename = '.console'
    openflags = 'rw'
    
    def __init__(self, stdin=None, stdout=None):
        """
        The optional arguments stdin and stdout
        specify alternate input and output file objects; if not specified,
        sys.stdin and sys.stdout are used.
        """
        import sys
        if stdin is not None:
            self.stdin = stdin
        else:
            self.stdin = sys.stdin
        if stdout is not None:
            self.stdout = stdout
        else:
            self.stdout = sys.stdout
        
        self.use_rawinput = True


    def read(self):
        return self.stdin.read()
    
    def readline(self):
        self.stdin.readline()
        
    def readlineprompt(self, prompt):
        if self.use_rawinput:
            try:
                line = raw_input(prompt)
            except EOFError:
                line = 'EOF'
        else:
            self.stdout.write(prompt)
            self.stdout.flush()
            line = self.stdin.readline()
            if not len(line):
                line = 'EOF'
            else:
                line = line[:-1] # chop \n
        return line


    def write(self, s):
        self.stdout.write(s)
        
    def writeline(self, s):
        self.stdout.write(s+'\n')
        

    def WriteFromLayout(self, layout):
        """
        walk through the rows of the given layout object, and write them
        to this stream object.
        """
        # GetLines returns a line at a time
        # this is more efficient than getting it all into one string and then writing it
        for row in layout.GetLines(self.formattype):
            self.writeline(row)


#--------------------------------------------------------------------------


class Csv(Stream):
    """
    Comma-separated values file.
    """
    extensions = 'txt,csv'
#    formattype = 'ascii'
    formattype = 'asciiNoCR' # \n's not allowed by excel!
    layouttype = 'Table'
    fielddelim = ','
    
    def WriteFromLayout(self, layout):
        import csv
        writer = csv.writer(self.file)
        # GetRows returns one row of Data objects at a time
        nlines = 0
        for row in layout.GetRows(Csv.formattype):
            # row is a list of Data objects
            # really need to translate it to a list of strings (via formattype) for output.
            ##, this is where we need to translate any \n's to [CR] or some such.
            for ncol in range(len(row)):
                data = row[ncol]
                s = data.GetString(Csv.formattype)
                row[ncol] = s
            writer.writerow(row)
            nlines += 1
        return 'Wrote %d lines.' % nlines

    ## def __iter__(self):
        ## return self.file.__iter__
    ## def next(self):
        ## return self.file.next

    ## def ReadToLayout(self):
        ## """
        ## read from this stream to a layout object 
        ## """


#--------------------------------------------------------------------------

class Tab(Stream):
    """
    Tab-delimited text files
    """
    extensions = 'txt'
#    formattype = 'ascii'
    formattype = 'asciiNoCR' # \n's not allowed by excel!
    layouttype = 'Table'
    fielddelim = '\t'

    def WriteFromLayout(self, layout):
        import csv
        writer = csv.writer(self.file, delimiter='\t')
        nlines = 0
        # GetRows returns a row at a time
        for row in layout.GetRows():
            writer.writerow(row)
            nlines += 1
        return 'Wrote %d lines.' % nlines


#--------------------------------------------------------------------------

class Ini(Stream):
    """
    Ini file format (aka cfg files)
    """
    extensions = 'txt,ini,cfg'
    formattype = 'ascii'
    layouttype = 'Ini'
    fielddelim = ''

    def WriteFromLayout(self, layout):
        
        import ConfigParser 
        config = ConfigParser.ConfigParser()
        
        nobjs = 0
        for row in layout.GetRows():
            config.add_section("book")
            nobjs += 1
            for prop in obj:
                config.set("book", "title", "the python standard library")
                
        writer = csv.writer(self.file, delimiter='\t')
        nlines = 0
        # GetRows returns a row at a time
        for row in layout.GetRows():
            writer.writerow(row)
            nlines += 1

        # write to file
        config.write(self.file)
        return 'Wrote %d objects.' % nobjs


#--------------------------------------------------------------------------

class Html(Stream):
    extensions = 'htm,html'
    formattype = 'ascii'
    layouttype = 'Table'
    fielddelim = ''
    
    
class Log(Stream):
    extensions = 'txt'
    formattype = 'ascii'
    layouttype = 'Log'
    fielddelim = ''
    

class Xml(Stream):
    extensions = 'xml'
    formattype = 'ascii'
    layouttype = 'Xml'
    fielddelim = ''


class Binary(Stream):
    extensions = 'b'
    formattype = 'binary'


class Gedcom(Stream):
    extensions = 'ged'
    formattype = 'ascii'


class Rtf(Stream):
    extensions = 'rtf'
    formattype = ''


class Pdf(Stream):
    extensions = 'pdf'
    formattype = ''
    
    
#--------------------------------------------------------------------------

def Test():
    
    import Abby
    import Commands
    
    filename = 'stuff.abby'
    abby = Abby.Abby()
    abby.Open(filename, False)
    
    print 'Test console...'
    stream = Console()
    print 'stream:',stream
    stream.writeline('hello!')
    print
    
    print 'Get some objects to export...'
    fish = abby.Get(exactname='fish')
    cmd = Commands.List(abby, fish)
    print cmd
    layout = cmd.Do()
    print layout.ob
    print

    print 'Test the stream factory...'
    filename = 'testcsv.txt'
    stream = Factory(filename, 'w')
    print 'stream:',stream
    print

    print 'Test writing to csv file...'
    status = stream.WriteFromLayout(layout)
    print status
    print
    
    print 'Test writing to tabdelim file...'
    filename = 'testtabs.txt'
    stream = Factory(filename, 'w', 'Tab')
    print 'stream:',stream
    status = stream.WriteFromLayout(layout)
    print status
    print
    
    abby.Close(False)  # discard all changes
    
if __name__=='__main__':
    Test()

