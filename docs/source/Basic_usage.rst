================
Using ``emmaze``
================

Introduction
------------

Basic usage
-----------
``emmaze`` can be used from the command line. When run without any options, it
produces a 10 by 10 maze without any exits and prints the maze as text art to
the standard output.

.. code-block:: console

    $ ./emmaze.py
    #####################
    #     #             #
    ##### # ######### # #
    #   # #     #     # #
    # ### ##### # ##### #
    # # # #   # # # #   #
    # # # # # ### # #####
    # #     #     #     #
    # ####### # ##### # #
    #       # # #     # #
    # ##### # ### ### # #
    # #     #     # # # #
    # # ### # ##### # # #
    # # #   # #     # # #
    ### # ##### ### # # #
    #   #       # #   # #
    # ########### ##### #
    # #             #   #
    # ########### # # ###
    # #           #     #
    #####################

To change the number of rows and columns, use the ``-r [number]`` and ``-c
[number]`` options, respectively.

.. code-block:: console

    $ ./emmaze.py -r 5 -c 25
    ###################################################
    #     #   #   #   #   #               #         # #
    # ### # # # # ### # # # ############# # ####### # #
    #   # # #   #   #   # # #         #     #   #     #
    ### # # ### ### ##### # ### ##### ####### # # ### #
    # # #   #     #       #     #   #     # # #   # # #
    # # ######### ######### ##### # ##### # ####### # #
    # # #       #           #     #   # # #     #   # #
    # # ##### # ################# ### # # # ### # ### #
    #         #                   #     #   #     #   #
    ###################################################

Exits
-----
To make a maze with exits, use option ``--[direction]-exit [number]``, where
``[direction]`` is ``north``, ``south``, ``east``, or ``west``, and ``[number]``
is the location along the wall. For example, to place an exit in the 8th
location along the west wall, use ``--west-exit 8``. (Note the locations are
zero-indexed.)

.. code-block:: console

    $ ./emmaze.py -r 9 -c 25 --west-exit 8 --east-exit 0
    ###################################################
    #   #       #     #   # #                     #    
    ### ####### # ### ### # # ############# ##### # # #
    #         # # #       # # #           #     #   # #
    # ####### # # ######### # # # # ########### ##### #
    #   #             #     # # # # #   # # # # #     #
    ### ############# ### ### # # ### ### # # # ### ###
    # #           #           # #   # # # # # # # #   #
    # ########### ############### # # # # # # # # #####
    #         #                 # # #   #     #   #   #
    # # ####### ##### ######### # # # ### ####### ### #
    # #         #   #         # # # #   #       #     #
    # ########### # ### ##### # ### ### ##### #########
    # # #   #   # #     #     #   #   #               #
    # # # # ### # ####### # ### # ### ### ########### #
    # # # #     # #       # #   #     #   #   #     # #
    # # # ### ### ######### # ######### # ### ### # # #
        #   #     #         #           #       # #   #
    ###################################################

Output as graphics
------------------
To output a maze as an SVG file, use the options ``-t svg -o [filename]``. 

.. code-block:: console

    $ ./emmaze.py -r 9 -c 25 --west-exit 8 --east-exit 0 -t svg -o my_maze.svg
    $ file my_maze.svg
    my_maze.svg: SVG Scalable Vector Graphics image

.. image:: my_maze.svg
   :height: 100px
   :width: 260px

Customize cell and wall size
----------------------------

Solutions
---------
You can produce a solution as well by using the ``--solutions`` option.

JSON support
------------
Mazes can be output and then later input in JSON format. To output as JSON, use
the options ``-t json -o [filename]``. To import, use the option 
``-j [filename]``.
