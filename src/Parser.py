
"""
Parser

"""


#. would be best to generate this file by walking through code and comments in Commands.py
#. using global abby reference


from ply import lex
from ply import yacc


import Plurals
import Commands
import Objects



import logging
log = logging.getLogger('')
log.debug('loading parser.py')



#, move to library
def flatten(L):
    if not isinstance(L,list): return [L]
    if L == []: return L
    return flatten(L[0]) + flatten(L[1:])
        


class ParserError(Exception):
    def __init__(self, arg=None):
        self.arg=arg
    def __str__(self):
#        return 'ParserError: %s' % str(self.arg)
        return str(self.arg)



#------------------------------------------------------------------------------
# Tokenizer/depluralizer
#------------------------------------------------------------------------------


keywords = ['it','them','to','from','as','all','group','sort','by','on','off','with','in']

verbs = [
    'add',
    'debug',
    'delete',
    'edit',
    'export',
    'find',
    'help',
    'import',
    'list',
    'load',
    'lookup',
    'put',
    'quit',
    'quiz',
    'random',
    'redo',
    'remove',
    'save',
    'set',
    'show',
    'undo',
    'verify'
    ]


punctuation = [
    'dash',
    'period',
    'comma',
    'equals'#,
#    'exclamation'
    ]
    

types = ['integer','string','date','filename','filetype','object','type']
## #    'PROPERTY',



# List of token names. This is always required.
# Defines all of the possible token names that can be produced by the lexer.
tokens = []
#. tokens.append(verbs.upper())  ?
for w in keywords:
    tokens.append(w.upper())
for w in verbs:
    tokens.append(w.upper())
for w in punctuation:
    tokens.append(w.upper())
for w in types:
    tokens.append(w.upper())




#--------------------------

filetypes = ['csv','tab','ini','cfg','html','xml','human']

#datewords = ['today','tomorrow','yesterday',
        #'sun','mon','tue','wed','thu','fri','sat']


# Regular expression rules for simple tokens.
# Each of these rules are defined by making declarations with a special 
# prefix t_ to indicate that it defines a token. 
# In this case, the name following the t_ must exactly match one of the 
# names supplied in tokens.
# Note: These are processed AFTER the tokens defined in functions, below.
#t_STRING = r"\'[^\']*\'"
t_DASH = '-'
#t_PERIOD = '\.' # moved below  # bug: had a plain period, forgot that it meant any character!!
t_COMMA = ','
t_EQUALS = '='
#t_EXCLAMATION = '!'
#t_OR = r'or'

# Regular expression rules with some action code.
# If some kind of action needs to be performed, a token rule can be specified 
# as a function. 
# The regular expression rule is specified in the function documentation string. 
# The function always takes a single argument which is an instance of LexToken. 
# This object has attributes of t.type which is the token type, t.value which 
# is the lexeme, and t.lineno which is the current line number. By default, 
# t.type is set to the name following the t_ prefix. The action function can 
# modify the contents of the LexToken object as appropriate. However, when it 
# is done, the resulting token should be returned. If no value is returned by 
# the action function, the token is simply discarded and the next token read. 

# for each token, set t.type and t.value
# eg 
# t.type = OBJECT
# t.value = obj


# Numeric Date
#def t_DATE


# Numbers
def t_INTEGER(t):
    r'[0-9]+'
    try:
        t.value = int(t.value)
    except ValueError:
        print "Line %d: Number %s is too large!" % (t.lineno,t.value)
        t.value = 0
    return t

def t_PERIOD(t):
    r'\.'
    return t


# Note: These exit through t_WORD, which gets a shot at recognizing the 
# string as an object name! 
# Will return STRING as token type, not LONGSTRING or SHORTSTRING!

## def t_STRING(t):
    ## # string surrounded by single or double quotes, 
    ## # with any character but quote or \ inside them.
    ## r"  \'[^\'\\]*\'  | \"[^\"\\]*\"  " 
    ## t.value = t.value[1:-1]  # remove quotes!
    ## return t_WORD(t)

def t_LONGSTRING(t):
    # string surrounded by triple single or double quotes, 
    # with any character but \ inside them.
    # Note: This must go before the shortstring, so that ''' is not caught there(?)
    r"  \'\'\'[^\\]*\'\'\'  | \"\"\"[^\\]*\"\"\"  " 
    t.value = t.value[3:-3]  # remove quotes!
    return t_WORD(t)
    
def t_SHORTSTRING(t):
    # string surrounded by single or double quotes, 
    # with any character but quote or \ inside them.
    #. also exclude linefeeds
    r"  \'[^\'\\]*\'  | \"[^\"\\]*\"  " 
    t.value = t.value[1:-1]  # remove quotes!
    return t_WORD(t)
    
    

def t_WORD(t):
    # Note: This never returns WORD as a token type. 
    # Will return STRING, or a verb name, or a keyword name, or OBJECT, etc.
#    r'[a-zA-Z]+'  # a single word  
    r'[a-zA-Z_]+'  # a single word  
#    r'[a-z\.A-Z]+'  # a single word  
#    r'[a-z\.A-Z_]+'  # a single word  
    
    t.type = 'STRING' # default, if not recognized as object name
    s = t.value.lower()  # for case-insensitive comparisons

    if s in verbs:
        #. actually use the string from the verbs list instead...
        t.type = s.upper() # upper case version of verb

    elif s in keywords:
        #. actually use the string from the list instead...
        t.type = s.upper()

        if t.type=='IT':
            t.value = abby.it
            #, raise if len not 1
    
        if t.type=='ALL':
            t.value = abby.all #... cool! 
            
        #. bombs, thinks t.value is a string?
        elif t.type=='THEM':
            t.value = abby.it
            #, raise if len not >1
    

    #elif s in datewords:
        #t.type = 'DATE'
        ##. actually use the string from the list instead...
        #t.value = s.capitalize() # eg 'Today', 'Mon'

    elif s in filetypes:
        t.type = 'FILETYPE'
        t.value = s.capitalize() # eg 'Csv'

    else:
        # see if we have an abby object
        obj = RecognizeObject(s)
        if obj:
            t.type = 'OBJECT'
            t.value = obj
#,?            t.value = Data.Link(obj)

            # get the type of the object
            #. look in abby word index to see what type of word we have...
            ## wordtype = obj.type
            #t.wordtype = wordtype  #. can we do this? NO!!! must do...
            #t.value = (s, obj, wordtype)

        # tried putting keyword search here, but still had problems
        # because was treating BY as a keyword, not a string, which is what
        # the SET command was expecting for a propvalue...
        
        ## else:
            ## # not an object name or anything else we can recognize, 
            ## # so just call it a string, and wrap it in a Data object.
            ## t.value = Data.String(t.value)
            
    return t



def RecognizeObject(s):
    """
    Try to recognize the given string as part of an object name.
    """
    #. could find more than one match - for now, just return first one
    #. also get the object's type! (obj.type) eg "Command" or "Type" or "Book"
    # (may have more than one)
    rs = abby.Get(exactname=s)
    if not rs:
        # lookup failed, so try depluralizing the word
        s = Plurals.Depluralize(s)
        rs = abby.Get(exactname=s)
#    obj = rs[0]
#    return obj
    return rs


# A string containing ignored characters (spaces and tabs)
# The special t_ignore rule is reserved by lex.py for characters that should 
# be completely ignored in the input stream. Usually this is used to skip over 
# whitespace and other non-essential characters. Although it is possible to 
# define a regular expression rule for whitespace in a manner similar to 
# t_newline(), the use of t_ignore provides substantially better lexing 
# performance because it is handled as a special case and is checked in 
# a much more efficient manner than the normal regular expression rules. 
t_ignore = ' \t' # space and tab
#t_ignore = ' \t,' # space and tab and comma (for now)


# Define a rule so we can track line numbers properly.
# This just discards the token.
## def t_newline(t):
    ## r'\n+'
    ## t.lineno += t.value.count("\n")
    ## print
    
# Error handling rule
# The t_error() function is used to handle lexing errors that occur when 
# illegal characters are detected. In this case, the t.value attribute contains 
# the rest of the input string that has not been tokenized. 
def t_error(t):
    # We simply print the offending character and skip ahead one character.
    print "!Illegal character '%s'" % t.value[0]
    t.skip(1)





#------------------------------------------------------------------------------
# Parser
#------------------------------------------------------------------------------

# Syntax is usually specified in terms of a context free grammar (CFG). 
# Each grammar rule is defined by a Python function where the docstring to 
# that function contains the appropriate context-free grammar specification.

# For tokens, the "value" in the corresponding p[i] is the same as the value 
# of the p.value attribute assigned in the lexer module. For non-terminals, 
# the value is determined by whatever is placed in p[0] when rules are reduced. 
# This value can be anything at all. However, it probably most common for the 
# value to be a simple Python type, a tuple, or an instance.

# The first rule defined in the yacc specification determines the starting 
# grammar symbol.

# t_ = token
# p_ = production


## # abstract syntax tree classes:
## class Node:
    ## def __init__(self,type,children=None,leaf=None):
         ## self.type = type
         ## if children:
              ## self.children = children
         ## else:
              ## self.children = []
         ## self.leaf = leaf


# grammar:

## def p_sentences(p):
    ## '''sentences : sentence
            ## | sentences PERIOD sentence
            ## '''
## #            | empty
    ## if (len(p.slice)==2):
        ## p[0] = [p[1]]
    ## else:
        ## #, probably a better way than this...
        ## p[0] = flatten([p[1],p[2]])  
        ## # props.words.append(p[1])
    
def p_sentence(p):
    '''sentence : add_stmt
            | debug_stmt
            | delete_stmt
            | edit_stmt
            | expression_stmt
            | export_stmt
            | find_stmt
            | import_stmt
            | list_stmt
            | lookup_stmt
            | quit_stmt
            | quiz_stmt
            | random_stmt
            | save_stmt
            | set_stmt
            | show_stmt
            | verify_stmt
            | put_stmt
            '''
#            | remove_stmt
#            | shell_stmt
    p[0] = p[1]  # ie a cmd object
    log.debug('p_sentence: %s', p[0])


def p_add_stmt(p):
    '''add_stmt : ADD adjectives name description'''# assignment_clause'''
    # eg   "add pphys hw 'ch3:1,2,8,9' due friday"
    n = len(p.slice)
    type = ''  # this has been subsumed in adjectives...
    adjectives = p[2] # list of objects, or empty list
    name = p[3]  # string
    description = p[4] # string or None
#    assignments = p[5]  # list of Set cmds? or empty list
#    cmd = Commands.Add(abby, type, name, description, adjectives, clauses)
    cmd = Commands.Add(abby, type, name, description, adjectives)
    p[0] = cmd    
    log.debug('p_add_stmt: %s',p[0])


def p_debug_stmt(p):
    '''debug_stmt : DEBUG ON
            | DEBUG OFF
            '''
    if (p[2]=='on'):
        debug = True
    else:
        debug = False
    cmd = Commands.Debug(abby, debug)
    p[0] = cmd
    
    
def p_delete_stmt(p):
    '''delete_stmt : DELETE objectref'''
    obj = p[2]
    p[0] = Commands.Delete(abby, obj)


def p_edit_stmt(p):
    '''edit_stmt : EDIT objectref'''
    obj = p[2]
    p[0] = Commands.Edit(abby, obj)


def p_expression_stmt(p):
    '''expression_stmt : reference
                '''
    # for now, this can be an object reference or attribute reference,
    # eg methanol, or methanol.etymology.
    # evaluates to the 'value' of the object or attribute.
    ref = p[1]
    p[0] = Commands.Expression(abby, ref)
    

def p_export_stmt(p):
    '''export_stmt : EXPORT adjectives tofilename asfiletype'''
    #, ambiguous: 'export physics' (ie export the physics subject or all objects 
    # with subject=physics?). we're treating it as the latter, which is probably fine?
    # eg "export to 'test.txt' as csv"?
    objects = p[2]
    filename = p[3]
    filetype = p[4]
    #, handle errors here?
#    assert(filename,'hello?')
#    if not filename: raise SyntaxError('hello?')
#    p[0] = Commands.Export(abby, filename, objects) # careful of order here!
    p[0] = Commands.Export(abby, filename, filetype, objects) # careful of order here!
    log.debug('p_export_stmt: %s',p[0])
    
## def p_exportcmd_error(p):
    ## '''exportcmd_error : EXPORT adjectives error'''
    ## raise SyntaxError('hello?')


def p_find_stmt(p):
    '''find_stmt : FIND STRING
                '''
    s = p[1]
    p[0] = Commands.Find(abby, s)
    

def p_import_stmt(p):
    '''import_stmt : IMPORT filename asfiletype'''
    filename = p[2]
    filetype = p[3]
    p[0] = Commands.Import(abby, filename, filetype)
    log.debug('p_import_stmt: %s',p[0])
    
    
def p_list_stmt(p):
#    '''list_stmt : LIST adjectives groupby sortby showprops'''
#    '''list_stmt : LIST adjectives clauses groupby sortby showprops'''
    '''list_stmt : LIST adjectives comparisons groupby sortby showprops'''
    # > list all sort by name
    # > list projects with rating 3+
    # > list all with date
    n = len(p.slice)
    adjectives = p[2]  # ob
    comparisons = p[3]  # eg "with date" or None
    groupby = p[4]
    sortby = p[5]
    showprops = p[6]
    cmd = Commands.List(abby, adjectives, comparisons, groupby, sortby, showprops)
    p[0] = cmd
    log.debug('p_list_stmt: %s',p[0])
    
    
def p_lookup_stmt(p):
    '''lookup_stmt : LOOKUP objectref'''
    obj = p[1]
    p[0] = Commands.Lookup(abby, obj)


def p_put_stmt(p):
    '''put_stmt : PUT objectrefs IN adjectives'''
    objects = p[2]
    adjectives = p[4]
    cmd = Commands.Put(abby, objects, adjectives)
    p[0] = cmd
    log.debug('p_put_stmt: %s',p[0])


def p_quit_stmt(p):
    '''quit_stmt : QUIT'''
    p[0] = Commands.Quit()
    
    
def p_quiz_stmt(p):
    '''quiz_stmt : QUIZ adjectives showprops'''
    adjectives = p[2]
    properties = p[3]
    #, really only want max of two properties to be entered here...
    # Quiz constructor could raise an error? raise a parser error?
    assert(len(properties)==2)
    p[0] = Commands.Quiz(abby, adjectives, properties)
    log.debug('p_quiz_stmt: %s',p[0])
    
    
def p_random_stmt(p):
    '''random_stmt : RANDOM adjectives'''
    adjectives = p[2]
    p[0] = Commands.Random(abby, adjectives)
    
    
def p_save_stmt(p):
    '''save_stmt : SAVE'''
    p[0] = Commands.Save(abby)
    
    
def p_set_stmt(p):
    ## '''set : SET objectrefs property TO STRING'''
    ## obj = p[2]
    ## propname = p[3]
    ## propvalue = p[5]
    ## p[0] = Commands.Set(abby, obj, propname, propvalue)
    ## '''set : SET property TO STRING'''
#    '''set_stmt : SET property TO propvalue'''
    '''set_stmt : SET attributeref TO propvalue
                | attributeref EQUALS propvalue
                '''
    # limit to attributerefs and propvalues for now - 
    # setting an objectref to something could come later
    n = len(p.slice)
    if (n==5):
        attrib = p[2]
        propvalue = p[4]
    else:
        attrib = p[1]
        propvalue = p[3]
#    p[0] = Commands.Set(abby, obj, prop, propvalue)
    p[0] = Commands.Set(abby, attrib, propvalue)

    log.debug('p_set_stmt: %s',p[0])
    
    
## def p_shell_stmt(p):
    ## '''shell_stmt : EXCLAMATION STRING'''
    ## s = p[2]
    ## p[0] = Commands.Shell(s)
    
    
def p_show_stmt(p):
#    '''show_stmt : SHOW OBJECT
#            | OBJECT
#    '''show_stmt : OBJECT
#            | objectid
    '''show_stmt : objectref
            | attributeref
            '''
    #, the word 'show' is optional
    n = len(p.slice)
    if n==3:
        ob = p[2]
    else:
        ob = p[1]
    cmd = Commands.Show(abby, ob)
    p[0] = cmd
    log.debug('p_show_stmt: %s',p[0])
    

def p_verify_stmt(p):
    '''verify_stmt : VERIFY'''
    cmd = Commands.Verify(abby)
    p[0] = cmd


#--------------------------------------------------------------------------------

    
def p_adjectives(p):
    '''adjectives : objectrefs'''
    # ie just an alias for objectrefs for now
    # as long as they are object references, they could be adjectives (ie property values)
    p[0] = p[1]
    log.debug('p_adjectives: %s',p[0])


    
def p_asfiletype(p):
    '''asfiletype : AS FILETYPE
            | empty
            '''
    n = len(p.slice)
    isempty = (n==2)
    if isempty:
        p[0] = None
    else:
        p[0] = p[2]  # filetype as string, eg 'Csv', 'Html'
    log.debug('p_asfiletype: %s',p[0])


## def p_assignment_clause(p):
    ## '''assignment_clause : empty
        ## '''
    ## p[0] = None


def p_attributeref(p):
    '''attributeref : propertyref
            | PERIOD propertyref 
            | objectref PERIOD propertyref
            '''
    # eg "methanol.etymology", "etymology" ("it." implied), ".etym"
    n = len(p.slice)
    if n == 2:
        obj = abby.it # "it." is implied
        prop = p[1]
    elif n == 3:
        obj = abby.it # "it." is implied
        prop = p[2]
    else:
        obj = p[1]
        prop = p[3]
    attrib = Objects.Attribute(obj, prop)
    p[0] = attrib        
    log.debug('p_attributeref: %s',p[0])


def p_comparisons(p):
    #, should be [COMMA] comparison [COMMA] [comparisons]
    '''comparisons : comparison
            | comparison comparisons
            | empty
            '''
    n = len(p.slice)
    if n==2:
        if p[1]: # ie comparison
            clause = p[1]
            p[0] = comparison
        else: # empty
#            p[0] = []
            p[0] = Commands.Comparisons() # empty list
    else:
        #. yuck - fix this
        comparison1 = p[1]
        comparison2 = p[2] # this could be single or plural...
        if isinstance(comparison2, Commands.Comparisons):
            comparisons = comparison2
            comparisons.append(comparison1)
        else:
            comparisons = Commands.Comparisons()
            comparisons.append(comparison2)
            comparisons.append(comparison1)            
        #list = flatten([p[1],p[2]])
        #p[0] = Commands.Comparisons(list)
        p[0] = comparisons
    log.debug('p_comparisons: %s',p[0])


def p_comparison(p):
    # [empty | [COMMA] phrase]
    '''comparison : COMMA comparison1
                | WITH comparison1
                | comparison1
                | empty
                '''
    n = len(p.slice)
    if n==3:
        p[0] = p[2]
    else:
        p[0] = p[1]
    log.debug('p_comparison: %s',p[0])


def p_comparison1(p):
    '''comparison1 : propertyref propvalue
                | propertyref
                | empty
                '''
    # eg rating '***'
    #, could also throw in an OPERATOR token to handle ==, <, etc
    n = len(p.slice)
    operator = '==' # default operator
    if n==3:
        p[0] = Commands.Comparison(p[1],operator,p[2])
    else:
        if p[1]: # property
#            p[0] = Commands.Comparison('self',operator,p[1]) # ie let comparison get propname
#            p[0] = Commands.Comparison(p[1],'!=','')
            p[0] = Commands.Comparison(None,operator,p[1]) # ie let comparison get propname
        else: # empty
#            p[0] = None
            p[0] = Commands.Comparison()
    log.debug('p_comparison1: %s',p[0])


def p_date(p):
    '''date : DATE'''
    s = p[1]
    p[0] = Data.Date(s)
    log.debug('p_date: %s',p[0])


def p_description(p):
    '''description : STRING
            | empty'''
    p[0] = p[1]
    log.debug('p_description: %s',p[0])
    

def p_filename(p):
    '''filename : STRING
            | STRING PERIOD STRING
            '''
    n = len(p.slice)
    if (n==2):
        p[0] = p[1]
    else:
        p[0] = p[1] + p[2] + p[3]
    log.debug('p_filename: %s',p[0])
    

def p_groupby(p):
    '''groupby : GROUP BY properties
            | empty
            '''
    #. strictly speaking, objnames should be propnames - enforce somehow?
    # rather than just return the objects with no info about what to do with them,
    # should set some groupby property value to them...
    n = len(p.slice)
    isempty = (n==2)
    if isempty:
        p[0] = []
    else:
        properties = p[3]
        p[0] = properties
    log.debug('p_groupby: %s',p[0])
    
    
def p_name(p):
    '''name : STRING'''
    p[0] = p[1]
    log.debug('p_name: %s',p[0])
    
    
def p_objectref(p):
    '''objectref : OBJECT
                | objectid
                | IT
                | THEM
                | ALL
                '''
    p[0] = p[1]
    log.debug('p_objectref: %s',p[0])


def p_objectid(p):
    '''objectid : INTEGER'''
    id = p[1]
    rs = abby.Get(id=id)
    p[0] = rs
    log.debug('p_objectid: %d=%s',id,p[0])
    
        
def p_objectrefs(p):
    '''objectrefs : objectref
            | objectref objectrefs 
            | objectref COMMA objectrefs 
            | empty
            '''
    # fyi first thing found is the empty one...
    n = len(p.slice)
    for i in range(n):
        log.debug('p[%d]=%s' %(i,p[i]))
    if n == 2:
        if p[1]: # objectref
            p[0] = p[1]
        else: # empty
            p[0] = Objects.Objs()
    elif n==3: # no comma
        rs1 = p[1]
        rs2 = p[2]
        rs2.extend(rs1)
        p[0] = rs2
    else: # with comma
        rs1 = p[1]
        rs2 = p[3]
        rs2.extend(rs1)
        p[0] = rs2
        
    log.debug('p_objectrefs: %s',p[0])


def p_properties(p):
    '''properties : objectrefs'''
    # ie just an alias for objectrefs for now
    p[0] = p[1]
    log.debug('p_properties: %s',p[0])


def p_propertyref(p):
    '''propertyref : objectref'''
    # just an alias for now
    #, ensure that the object is a property object!
    p[0] = p[1]
    log.debug('p_propertyref: %s',p[0])


## def p_propname(p):
    ## '''propname : STRING'''
    ## p[0] = p[1]


def p_propvalue(p):
    '''propvalue : objectref
            | STRING
            | INTEGER
            | date
            | empty
            '''
    #. this should return a data object!
    #. sometimes will want to use the string literal instead of an object it happens to refer to!
    # this could return actual propvalue that setvalue will use...
    #if OBJECT:
        #p[0] = Data.Link(p[1])
        #p[0] = GetInternalName(p[1].name)
    p[0] = p[1]
    log.debug('p_propvalue: %s',p[0])



def p_reference(p):
    '''reference : objectref
                | attributeref
                '''
    p[0] = p[1]
    
    
    
def p_showprops(p):
    '''showprops : SHOW properties
            | SHOW ALL
            | empty'''
    #, note: show is also a verb - will this keyword cause problems?
    # this is used by List and Quiz 
    n = len(p.slice)
    isempty = (n==2)
    if isempty:
        #. bad to have this here!
#        p[0] = 'default'  
        p[0] = 'all'
    else:
        p[0] = p[2]
    log.debug('p_showprops: %s',p[0])


def p_sortby(p):
    '''sortby : SORT BY properties
            | BY properties
            | empty
            '''
    n = len(p.slice)
    isempty = (n==2)
    if isempty:
        p[0] = []
    elif n==4: 
        properties = p[3]
        p[0] = properties
    else: # n==3: 
        properties = p[2]
        p[0] = properties
    log.debug('p_sortby: %s',p[0])




## def p_string(p):
    ## '''string : SHORTSTRING 
            ## | LONGSTRING'''
    ## p[0] = p[1]
    

def p_tofilename(p):
    '''tofilename : TO filename'''
            ## | empty'''
    ## n = len(p.slice)
    ## if n==2:
        ## p[0] = None
    ## else:
        ## p[0] = p[2]  # filename as string
    p[0] = p[2]  # filename as string
    log.debug('p_tofilename: %s',p[0])


## def p_with_clause(p):
    ## '''with_clause : WITH property
            ## | empty'''
    ## n = len(p.slice)
    ## isempty = (n==2)
    ## if isempty:
        ## p[0] = None
    ## else: 
        ## p[0] = p[2]  # prop reference
    ## log.debug('p_with_clause: %s',p[0])


    
#------------------------------------------------------------------------------

def p_empty(p):
    'empty :'
    return None
    
def p_error(t):
#    print "!Syntax error in parser at %s" % t
#    s = "Syntax error at %s" % t
    if t:
        s = "I don't understand what '%s' means." % t.value
    else:
        s = "Expected something more...?"
    raise ParserError(s)


#------------------------------------------------------------------------------
# Main entry point
#------------------------------------------------------------------------------

class Parser:
    def __init__(self, abbydb):

        # store 
        ## self.abby = abby
        global abby
        abby = abbydb
        
        # Build the lexer
        # To build the lexer, the function lex.lex() is used. This function uses Python 
        # reflection (or introspection) to read the the regular expression rules out of 
        # the calling context and build the lexer. 
        ## print "Building the lexer..."
        lex.lex()
#        lex.lex(debug=1)  # gain some additional debugging info
        self.lex = lex
        ## print
        
        ## print "Building the parser..."
        # By default, the yacc generates tables in debugging mode (which 
        # produces the parser.out file and other output). To disable this, use 
        # yacc.yacc(debug=0)
        #yacc.yacc()
        #yacc.yacc('SLR',1,mylex)
        yacc.yacc(method='SLR',debug=1)
        self.yacc = yacc
        ## print
        

    def Parse(self, s):
        """
        Parse the given sentence s using abby for word lookups, etc.
        Returns a Command object that can be run by cmd.Do()...
        Will throw ParserError exception on syntax error.
        """
        self.s = s
        cmd = yacc.parse(s) # might throw a parser exception
        
        ## try:
            ## cmd = yacc.parse(s)
        ## except ParserError,e:
            ## # print e
            ## # print 'Trying as shell command...'
            ## # parser didn't like it, so try it as a shell command
            ## #, then as a python command
            ## cmd = Commands.Shell(s)
            
            ## # try:
                ## # cmd = Commands.Shell(s)
            ## # except:
                ## # # now try it as a python command
                ## # raise ParserError('Unrecognized as villa command or valid system command')
            
        return cmd


#------------------------------------------------------------------------------

def Test():    
   
    import Abby
    
    filename = 'stuff.abby'
    abby = Abby.Abby()
    abby.Open(filename, False)

    # build lexer and parser
    parser = Parser(abby)
    print
    
    ## testlexer = False
    ## testparser = False    
    testlexer = True
    testparser = True
    
    ss = r"""
        debug on
        get.type=action
        """
    """
        list subjects
        1048
        put it in kalispell
        it
        put 1048, 1224 in kalispell
        them
        1048
        list subjects
        edit
        caffeine.etym='test'
        methanol.etym
        'methanol'.'etymology'
        debug off
        add quote '''For a moment, he hadn't the slightest idea. "Maybe," Tia had once said.''', author 'Escape to Witch Mountain'
        list classes
        list aas by symbol
        list with date sort by date
        list hw by date
        quiz aas show name, code
        quiz aas show name, symbol
        debug
        list aas
        debug
        add todo 'xerox stuff' at school
        add todo 'sign math minor' at school
        add todo 'get milk, cheese' at randalls
        list todo        
        add pphys hw 'read ch1', rating '***'
        'read ch1'
        list
        list types
        add pphys hw 'read ch1'
        list classes
        quiz terms
        neuro
        list projects
        list projects show all
        list projects sort by timeframe
        neomem
        set name to neofoo
        it
        list sort by name
        list sort by type,name
        add word aesiwe
        edit aesiwe
        list fun
        delete aesiwe
        question
        dir *.csv
        import testin.csv
        nleagh
        dir *.txt
        list
        list types
        add word classicalicious
        set neomem rating to '****'
        neomem
        import from testin.txt
        neomem
        show neomem
        it
        list subjects
        them
        list
        list equations
        list neomem tasks
        list today neomem tasks
        list groupby type
        list projects sort by timeframe
        add task 'do dishes'
        add project 'grow spinach'
        add 'notype!'
        add subject Biology aka bio 'Things that go crawling around...'
        add subject Science 'Everything under the sun...'
        bio
        random subject
        squamous
        bleargh!
        export
        """
        
    """
        list hw
        export them to testit.txt
        
        export to testout.txt
        export types to testoutcsv.txt
        export types to testouttab.txt as tab
        import from testin.txt
        """
        
    ss = ss.strip()
    ss = ss.split('\n')

    ## # Test lexer
    ## if testlexer:
        ## print "Testing the lexer..."
        ## for s in ss:
            ## s = s.strip()
            ## print '>',s
            ## # Give the lexer some input
            ## parser.lex.input(s)
            ## while True:
                ## # Get the next token (a LexToken instance), or None if at end of input. 
                ## tok = parser.lex.token()
                ## if not tok: break      # No more input
                ## print tok
            ## print
        ## print

    # Test parser
#    if testparser:
#    print "Testing the parser..."
    for s in ss:
        s = s.strip()
        log.debug('abby.it: %s',abby.it)
        print '>',s
        
        # test the lexer
        if testlexer:
            parser.lex.input(s)
            while True:
                # Get the next token (a LexToken instance), or None if at end of input. 
                tok = parser.lex.token()
                if not tok: break      # No more input
                log.debug(tok)
            print
            
        # parse the string
        if testparser:
            try:
                cmd = parser.Parse(s)
                log.debug('cmd: %s', cmd)
                if cmd:
                    log.debug('abby.it: %s',abby.it)
#                    layout = abby.Do(cmd)  # tie into command history
                    layout = cmd.Do()
                    log.debug('returns:')
                    print layout
                    log.debug('abby.it: %s',abby.it)
            # catch syntax errors
            except ParserError, e:
                print e
            # catch command errors
            except Abby.AbbyError, e:
                print e
    print
        
    abby.Close(False)  # discard all changes


if __name__=='__main__':
    Test()
    
