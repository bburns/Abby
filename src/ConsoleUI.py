
"""
ConsoleUI/Villa
Defines a console interface to Abby, like an Infocom game,
or an Apple II.

Villa contains a console and a parser.

The console is used for string input and output.

The parser takes a string and returns a Command object,
which is applied to Abby.

"""



# Python modules
import os

# Abby modules
import Commands
import Data
import Parser
import Streams



import logging
log = logging.getLogger('')
log.debug('loading ConsoleUI.py')


## import textwrap
## wrapper = textwrap.TextWrapper()
## wrapper.width = 100
## wrapper.replace_whitespace = False
#.. don't ignore newlines!
#      self.intro = textwrap.dedent("""\



"""
If completion is enabled, completing commands will be done automatically, 
and completing of commands args is done by calling complete_foo() with 
arguments text, line, begidx, and endidx. text is the string prefix we are 
attempting to match: all returned matches must begin with it. line is the 
current input line with leading whitespace removed, begidx and endidx are 
the beginning and ending indexes of the prefix text, which could be used 
to provide different completion depending upon which position the argument is in. 
"""



## def dprint(s):
    ## """
    ## debug print variable, eg
    ## dprint('x') will print 'x:' and value of x
    ## """
    ## print '%s:%s' % (s, str(eval(s)))



class ConsoleUI:
    
    def __init__(self, abby):

        log.debug('ConsoleUI init')
        
        self.abby = abby
        
        # get our parser object
        self.parser = Parser.Parser(abby)
        
        self.prompt = '> '
        
        date = Data.Date()
        self.intro = "\nWelcome to NeoMem Console\nUsing Abby (version %s)\n" % (abby.version)
        self.intro += str(abby) + '\n'
        self.intro += str(date) + '\n'
        
        # get our stream object (in this case, the console/stdio)
        #, this could be a PlainConsole, AnsiConsole, or HtmlConsole
        self.console = Streams.Console()

        # open transcript file
        self.transcript = open('transcript.txt','a') # a=append


    def Do(self):
        """
        Repeatedly issue a prompt, accept input, parse it into a command,
        execute the command and give feedback.
        Returns t/f to savechanges made.
        """


        # print intro
        self.Output(self.intro)
    
        # do loop
        while True:
            #,
            ## try:
                ## s = raw_input(self.prompt)
            ## except EOFError:
                ## s = 'EOF'
                
            # get input from user
#            input = raw_input(self.prompt)
            input = self.console.readlineprompt(self.prompt)
            
            # write the input to the transcript
            self.transcript.write(self.prompt + input)
            self.transcript.write('\n')
            
            if input:
                    
                try:
                    # Parse string and return a Command object which can be executed.
                    # If parser doesn't recognize the string, will build a Shell command.
                    cmd = self.parser.Parse(input)
                    log.debug('cmd: %s',`cmd`)
                    
                    #, parser could pull data from the console until it builds a command
                    # this would let it interrogate user until resolves ambiguities
    #                cmd = self.parser.ParseFromFile(console)
    #                cmd = self.parser.InputFrom(stream)
                
                    # handle quit
                    #, dubious
                    #, handle ConsoleUI-specific commands here?
                    # ie quit, save, ???
                    if isinstance(cmd, Commands.Quit):
                        break # ie break out of the while loop
                        
                    # execute the Command object
                    # may throw an AbbyError exception if database doesn't like it (caught below)
#,                    layout = self.abby.Do(cmd)
                    layout = cmd.Do()
                    log.debug('layout: %s',`layout`)
#                    print 'layout.ob:',`layout.ob`
                    output = layout.GetString()
                    if output=='': # shell will return blank string if unrecognized shell command
                        # failed as ConsoleUI command and shell command, so try as python expression
                        # eg good for calculator
                        try:
                            output = str(eval(s))
                        except:
                            output = 'Syntax Error (not recognized by ConsoleUI, shell, or Python)'
                    self.Output(output)
                    #, or 
    #                self.console.WriteFromLayout(layout)
    
                    #, get layout for a given type:
                    # objtype = obj in adjectives that is a type (ie .type = 'Type')
                    # - get a layout object saved with the typeobj, 
                    # eg has certain columns displayed,
                    # column widths, groupby and sortby orders, certain filter?...
                    # layout = objtype.layouts['Table']
    
                    # print abby status
                    #, rather, update the status bar of any window
    #                self.UpdateStatus()
                    
                # if parser raised an error (ie a syntax error), display the error and continue
                except Parser.ParserError, e:
                    self.Output(str(e))
                except Abby.AbbyError, e:
                    self.Output(str(e))
                except IOError, e:
                    # eg trying to import a file that doesn't exist
                    self.Output(str(e))
                except Exception, e:
                    #,
                    self.Output('WARNING: Caught an unhandled exception! Saving database...')
                    #. should first make a backup copy!
                    self.abby.Save()
                    self.Output(str(e))
                    raise
                
        #, ask user
        savechanges = True
        return savechanges


    def Output(self, s):
        """
        Output the given string to the terminal, with word wrapping.
        """
        ## list = wrapper.wrap(s)
        ## for line in list:
            ## print line
        ## # print a blank line if needed
        ## if line: print
        #.. ridiculous - wrapper is ignoring embedded newlines!!?
        # subclass and add an option, ?
        #print s
#        s = wrapper.fill(s)
#        print s
#        print
        self.console.writeline(s)
#        self.console.writeline('')

        # also write to transcript if enabled!
        self.transcript.write(s)
        self.transcript.write('\n')

        #. also debug output?
        #log.debug(s)


    def UpdateStatus(self):
        """
        Print out the current status of Abby.
        """
        #, eventually could subscribe to such notifications, print out?
        # but then might get out of order with other print messages...
        #, in debug mode could print more info (eg current obj etc)
        s = abby.status
        self.Output(s)



if __name__=='__main__':

    # this is not a test - this is the actual program...

    log.debug('run ConsoleUI main')

    import Abby

    # open database
    print 'opening database...'    
    filename = 'stuff.abby'
    abby = Abby.Abby()
#    abby.SetDebug(True)
    abby.Open(filename)

    # make our ui object and run it
    print 'running console...'
    ui = ConsoleUI(abby)
    savechanges = ui.Do()
    abby.Close(savechanges)
    
    print 'database closed'



"""
#for interactive stuff, run pyshell, and enter the following...

import Abby
abby=Abby.Abby()
abby.Open('stuff.abby')
ob=abby.Get(exactname='elec')
#(do stuff to ob now)

abby.Close()

"""

