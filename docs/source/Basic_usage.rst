================
Using ``emmaze``
================

``emmaze`` can be used from the command line. When run without any options, it
produces a 10 by 10 maze without any exits and prints the maze as text art to
the standard output.

To make a maze with exits, use option ``--[direction]-exit [number]``, where
``[direction]`` is ``north``, ``south``, ``east``, or ``west``, and ``[number]``
is the location along the wall. For example, to place an exit in the 8th
location along the west wall, use ``--west-exit 8``. (Note the locations are
zero-indexed.)

To output a maze as an SVG file, use the options ``-t svg -o [filename]``. 

To change the number of rows and columns, use the ``-r [number]`` and ``-c
[number]`` options, respectively.

You can produce a solution as well by using the ``--solutions`` option.

Mazes can be output and then later input in JSON format.