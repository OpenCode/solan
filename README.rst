Share your files in LAN
-----------------------

Solan is a simple and basic system to share files with other people in the same LAN

Installation
------------

Clone repository on your system and install it

::

    $ python3 setup.py install

Usage
-----

::

    $ solan [path_to_share]

and then open your browser and visit the url printed in your terminal

Examples:

::

    $ solan /tmp

or you can define a different port (standard is 8000)

::

    $ solan ~/Example/Share -p 8004

Remote access
=============

Enable remote with -r parameter

::

    $ solan -r /tmp
