
"""
Plurals
Handle pluralization/depluralization of words.

primarily concerned with depluralization for now
eg > list projects (need to identify singular form 
of projects as the type to search for)


#,
axes to axis
meshes to mesh
fishes to fish
geese to goose

"""


#. make this a class/object
#, of course could exchange with other languages eventually
#, best if information was stored in a text file and read in on init



def Depluralize(word):
    """
    Try to depluralize the given word, using standard English pluralizing rules,
    and an incomplete list of exceptions to the rules.
    """
    newform = word # default is to just stay as it is
    
    # these words are already singular (but end in -s)
    exceptions = ['physics','pants','scissors','s']
    if word in exceptions:
        newform = word

    # rule: -ies to -y
    # eg Libraries to Library
    elif word[-3:]=='ies':
        newform = word[:-3] + 'y'
    
    # rule: -sses to -ss
    # eg Classes to Class
    # can't just check for -es because, eg Types!->Typ
    elif word[-4:]=='sses':
        newform = word[:-2]
            
    # rule: -s to -
    # eg Tasks to Task
    elif word[-1:] == 's':
        newform = word[:-1]
    ## # -i to -us, eg torus, tori  or cactus, cacti
    ## elif word[-1:] == 'i':
        ## newform = word[:-1] + 'us'

    #, special cases

    return newform

        
        
if __name__=='__main__':

    # plurals
    # squamous - an exception
    testwords = [
            'socks','cows','physics','pants',
            'tori','data','libraries','classes','types',
            'properties','s',
            
            # bombs
            'squamous']

    print 'unknown -> depluralized...'
    for word in testwords:
        d = Depluralize(word)
        print word, '->', d

    
