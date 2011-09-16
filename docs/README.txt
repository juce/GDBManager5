GDB Manager 5                                            September 15, 2011
===========================================================================
Version 5.4.0


1. INTRODUCTION
---------------

GDB Manager is a GUI front-end for KitServer 5 GDB (Game DataBase). 
It simplifies the task of defining kit attributes, such as 3D-model of a 
shirt, collar type, name location, name shape, and some others.

GDB Manager will modify (and create, if necessary) the corresponding 
"config.txt" files. (Note that you need KitServer 5.1.2 or later in order
to see the effect of some attributes.)


2. USAGE
--------

Run GDBManager.exe. When run first time, it will ask you to select the
location of your "GDB" folder. After that it should show a directory-like
tree on the left side which enumerates all the kits in the GDB. You can
select a kit file there and set/modify attributes in the right panel.


3. KDB->GDB converter
---------------------

If you want to convert your existing KDB to new format GDB, you can use
"Import from KDB" action from "Tools" menu. This will start the converter
tool, which is implemented as a simple wizard. Follow the instructions 
on the wizard screens.


4. CREDITS
----------

Programming: juce
Third party tools and libraries: wxPython by Robin Dunn and Co.

===========================================================================


