
# Abby

Abby is a prototype for a console-based database from 2004, and includes several parts:


**Abby** is the database backend, using [Zodb](http://www.zodb.org/) to persist
objects to a file. It is a Python module, and can be accessed by importing it
and using the Python interface.

**Villa** is a console interface to Abby, allowing interactive access to the
database.

**Straylight** is a concept HTML console interface to Abby, similar to Villa but
handling formatted output and images, etc.

**NeoMem** would be modified to use Abby instead of the current backend called
Brooklyn, if there is any interest in maintaining such a user-interface.


## The problem

It's hard to enter lots of information in NeoMem.

I use 3x5 index cards to jot down thoughts, things to do, things to memorize for
school, and then when I get a chance, put them into NeoMem. It's hard to enter
stuff quickly though - it takes a long time to add new classes, navigate around,
create folders, etc.

So I have this backlog of information sitting on 3x5 cards.


## Transcript

It's always simpler to just look at an example rather than read a formal description, so here's
a sample session with Villa:


```
Welcome to Villa
Using Abby (version 0.1)
Abby database file 'stuff.abby', 226 objects.

> list todo
Name                           Altname      Type           Description
--------------------------------------------------------------------------------------------------------------------
make postcard posterboard                   Todo
upload site and setup.exe                   Todo

> add todo 'get plumbago for patio'
Added object 'get plumbago for patio'.

> add todo 'get small travel clock for library'
Added object 'get small travel clock for library'.

> list projects
Name                           Altname      Type           Description
--------------------------------------------------------------------------------------------------------------------
Abby                                        Project
Backpack cooler                             Project        set to 70deg or so, above dewpoint, so no condensation!?...
cold water dishwasher                       Project        washing dishes is wasteful of time, water, and heat ener...
dsim                                        Project        dielectric spectroscopy simulation
FileExtension                               Project        rclick file - edit extension. small c window program, us...
FolderIcon                                  Project        rclick folder, assign icon : choose icon in dialog, copy...
Gillan                                      Project        finish gillan's hands, put purple sky in background?
Home garbage decomposer                     Project        get energy out of all that sugar!
Hydroponics                                 Project        grow bean sprouts etc
Learn Cygwin                                Project        ie in place of installing Linux. will be very important ...
MetabolicSim                                Project        model energy flow, mito growth, glocose, creatine, ATP, ...
MicroAquarium                               Project        zoom in on pond scum, 100-300x, pan around, feed with su...
moss                                        Project        design 3d house and grounds, garden, maze, moss garden, ...
NeoMem                                      Project
pde                                         Project        pde solver. keep it simple - this is for educational pur...
ShellSpy                                    Project        listen in on windows explorer notifications, build a log...
SimCycle interface                          Project        simple serial port interface to get info from simcycle
Slanted Mousepad                            Project        to reduce wrist fatigue!
SlowBird                                    Project        film finches at high speed (with sound) and play back sl...
Smart Alarm Clock                           Project        set different times for different days, good for college...
Terrarium                                   Project        with lots of moss, little mushroom lights

> list neomem
Name                           Altname      Type           Description
--------------------------------------------------------------------------------------------------------------------
add a Popular/Favorites ta...               Enhancement
add button to toggle hidin...               Enhancement
setup forum                                 Todo

> list types
Name                           Altname      Type           Description
--------------------------------------------------------------------------------------------------------------------
Advice                                      Type
Amino Acid                                  Type
Compound                                    Type           most general term for a molecule, protein, etc
Disease                                     Type
Enhancement                                 Type
Equation                       eqn          Type
Event                                       Type           something that happened, or will happen
Fish                                        Type
Fun                                         Type
Get                            toget        Type           something to get at the store
Language                       lang         Type
Library                                     Type
Lookup                                      Type
Lost                                        Type
Movie                                       Type
Phrase                                      Type
Program                                     Type
Project                                     Type
Property                                    Type
Question                                    Type           some question that you want to research and find an answ...
Quote                                       Type
Reminder                                    Type           a future event that you want to be reminded about
Subject                                     Type
Task                                        Type
Term                                        Type
Timeframe                                   Type
Todo                                        Type           things to do
Toxin                                       Type
Type                                        Type
Unit                                        Type
Word                                        Type

> list fish
Name                           Altname      Type           Description
--------------------------------------------------------------------------------------------------------------------
Bosemani Rainbow                            Fish           very cool looking, $15, grows to 4 inches, ****
Otocinclus Catfish                          Fish
plecy                                       fish           this is some description
Veil Angelfish                              Fish

> plecy
Property             Value
--------------------------------------------------------------------------------
Name                 plecy
Altname
Type                 fish
Description          this is some description
Creationdate         Sun 22 Aug 2004 10:49:51 PM

> list subjects
Name                           Altname      Type           Description
--------------------------------------------------------------------------------------------------------------------
Art                                         Subject
Biology                        bio          Subject
Calculus                       calc         Subject
Chemistry                      chem         Subject
Electricity and Magnetism      em           Subject
Math                                        Subject
Music                                       Subject
Numerical Analysis             numeric      Subject
Physics                        phys         Subject
Trigonometry                   trig         Subject
Vector Analysis                             Subject        Deals with scalar fields, vector fields, and differentia...

> add subject Neuroscience aka neuro
Object 'Neuroscience' added.

> neuro
Property             Value
--------------------------------------------------------------------------------
Name                 Neuroscience
Altname              neuro
Type                 Subject
Description
Creationdate         Tue 24 Aug 2004 01:38:38 AM

> save
231 objects saved to file 'stuff.abby'.
>

------

> add word abulia, 'abnormal lack of ability to act or to make decisions'
Word 'abulia' added.

> add physics equation 'Clausius-Mossotti Equation', 'Gives molecular polarizability alpha in terms of number of particles per unit volume N and dielectric constant K.'
Equation 'Clausius-Mossotti Equation' added.

> list words
abulia    abnormal lack of ability to act or to make decisions
abyss    greek, without bottom
acerbic    acid in temper, mood, or tone
...

> quiz words
Definition of abulia:
a. acid in temper, mood, or tone
b. abnormal lack of ability to act or to make decisions
c. ...
d. ...
: a
Right!

```


## Install

Install Python 2.7, [Zodb](http://www.zodb.org/), and [ply (Python Lex Yacc)](https://github.com/dabeaz/ply):

    > pip install zodb
    > pip install ply


## Run

    > abby


## Exit

    > quit


## Goals

Goals for Abby:

- Keep it simple, like Python itself. ie don't proliferate a huge set of api methods
- Try to follow the way the brain organizes information if possible, i.e. fuzzily (a fuzzy database)

Goals for Villa:

- Acts as an external memory, simple to use
- Semi-natural language interface (like an old Infocom game)
- Able to publish objects to a website
- Task manager
- Help with learning and memorization
- Port to phone eventually


## Todo

- Add `help` command
- Merge with NeoMemRuby


## License

GPL

