=================================
Command line usage
=================================


Description
-----------

:program:`emmaze` generates random mazes and outputs them in various formats. It can also
import and solve mazes provided in the :doc:`JSON_maze_format`.

Example
-------

.. code-block::

   $ emmaze
   #####################
   #     #             #
   ##### # ##### ##### #
   #   # #   # # # #   #
   ### # # ### # # # ###
   #   # # #       #   #
   # ### ### ######### #
   # # #   # #       # #
   # # ### ### ### # # #
   # #         # # # # #
   # ########### # # # #
   #         #   # #   #
   ##### # # # # # # ###
   #   # # # # #   #   #
   # # ### # # ####### #
   # #   # # #   # #   #
   ### # # ##### # # ###
   #   # #       # # # #
   # ############# # # #
   #                   #
   #####################

   $ emmaze --rows 15 --cols 25 -t block --north-exit 0 --east-exit 14
   █ █████████████████████████████████████████████████
   █ █ █     █           █     █   █   █         █   █
   █ █ █ █ █ █ █████ ███ █████ █ ███ █ █ █ ███████ █ █
   █ █   █ █   █   █   █ █   █ █     █   █     █   █ █
   █ █████ █████ █████ █ ███ █ ███ ███████████████ ███
   █       █       █ █ █     █ █   █               █ █
   ███████████████ █ █ █ █████ █ ███ █████████ █████ █
   █             █   █ █       █     █       █       █
   █████████ ███ █ ███ █ █████ █ ███ █ █████ █ █████ █
   █       █ █ █   █   █ █   █     █     █ █ █ █   █ █
   █ █████ █ █ █ ███ ███ █ ███ █ █ █████ █ █ █████ █ █
   █     █ █ █   █     █ █     █ █     █ █ █ █     █ █
   █ ███ ███ █ ███ ███ █ █████ █ █████ █ █ █ █ ███████
   █ █ █     █ █     █ █     █ █     █ █   █   █     █
   █ █ ███ █████ █████ █████ █ ███ █ █ █ ███████████ █
   █ █   █   █   █         █ █ █   █ █ █             █
   █ ███ ███ █ ███ ███████ █ █ ███ █ █ ███ █████████ █
   █   █   █   █   █ █   █ █ █   █ █ █   █ █   █   █ █
   ███ █ █ █████ ███ █ ███ █ ███ █ █ ███ █ ███ ███ ███
   █     █ █     █   █   █ █   █ █ █   █ █     █ █   █
   ███████ █ █████ █ ███ █ ███ █ █ ███ █ ███████ ███ █
   █     █ █     █ █     █   █ █ █ █   █ █         █ █
   █ ███ ███████ █ █████ ███ █ █ █ █ ███ █ ███████ █ █
   █ █ █     █   █     █ █   █ █ █ █ █   █ █       █ █
   █ █ █████ █ █████████ █ ███ █ █ █ █ █████ ███████ █
   █ █   █ █   █       █     █ █ █ █ █       █       █
   █ █ █ █ █████ █ ███████████ █ █ ███████████ ███████
   █ █ █     █ █ █     █ █     █ █             █     █
   █ █████ █ █ █████ █ █ █ █████ █ ███████████████ █ █
   █ █     █         █     █     █                 █
   ███████████████████████████████████████████████████

Options
-------

.. program:: emmaze

.. option:: --help

   Show a summary of command line options and exit.

.. option:: --import_json <FILE>, -j <FILE>

   Import a maze from a JSON file in the :doc:`JSON_maze_format`.

.. option:: --rows <ROWS>, -r <ROWS>

   Specify the number of rows in the maze. If this argument is not used, a default of 10 is
   used.

.. option:: --cols <COLS>, -c <COLS>

   Specify the number of columns in the maze. If this argument is not used, a default of 10
   is used.

.. option:: --output_type <FORMAT>, -t <FORMAT>

   Specify the format for the output. Supported formats are:

   * ``text``: Output the maze as text with the character ``#`` as the walls.

   * ``block``: Output the maze as text with the character ``█`` (U+2588) as the walls.

   * ``svg``: Output in the Scalable Vector Graphics format. (To save to file, use
     the :option:`--output_file` option.)

   * ``json``: Output in the :doc:`JSON_maze_format`, for later use with the
     :option:`--import_json` option. (To save to file, use the :option:`--output_file`
     option.

.. option:: --output_file <FILE>, -o <FILE>

   Output to a file. If this option is not used, then the output is sent to the standard
   output.

.. option:: --solutions, -s

   Include the solutions in the output. If a maze is imported from JSON, solutions will
   be generated.

.. option:: --north-exit <COL>

   Place an exit on the north (top) wall in the specified column. Columns are zero-indexed
   starting from west (left).

.. option:: --east-exit <ROW>

   Place an exit on the east (right) wall in the specified row. Rows are zero-indexed
   starting from the north (top).

.. option:: --south-exit <COL>

   Place an exit on the south (bottom) wall in the specified column. Columns are
   zero-indexed starting for the west (left).

.. option:: --west-exit <ROW>

   Place an exit on the west (left) wall in the specified row. Rows are zero-indexed
   starting from the north (top).

.. option:: --copyright

   Show the :ref:`copyright and license information <license>` and exit.

.. option:: --version

   Show the version information and exit.


.. toctree::
   :maxdepth: 2
   :caption: Contents:
