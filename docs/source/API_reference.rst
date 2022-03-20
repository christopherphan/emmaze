=============
API Reference
=============


.. toctree::
   :maxdepth: 2
   :caption: Contents:

``maze``: Core functionality
=============================================================

.. automodule:: mazeing.maze

Type aliases
------------

.. py:data:: DIRECTION_TYPE

   The four main cardinal directions.

   :type: TypeAlias
   :value: Literal["north", "south", "east", "west"]

.. py:data:: DIAG_DIRECTION_TYPE

   Pairs of cardinal directions (used to represent intercardinal directions, e.g. northeast as ``("north", "east")``).

   :type: TypeAlias
   :value: tuple[DIRECTION_TYPE, DIRECTION_TYPE]

Classes
-------

.. autoclass:: DirectionInfo
   :members:

.. autoclass:: Maze
   :members:

.. autoclass:: MazeConstructor
   :members:

.. autoclass:: MazeExit
   :members:

.. autoclass:: MazeWorker
   :members:

.. autoclass:: Position
   :members:

.. autoclass:: WallLine
   :members:

Functions
---------

.. autofunction:: make_maze


``svgfunctions``: Helper for making HTML/XML/SVG documents
==========================================================

.. automodule:: mazeing.svgfunctions

Class
-----

.. autoclass:: Element
   :members:

``svgmazes``: Functionality to output mazes to SVG
==================================================

.. automodule:: mazeing.svgmazes

Type aliases
------------

.. py:data:: CornerPair

   :type: TypeAlias
   :value: tuple[maze.DIAG_DIRECTION_TYPE, maze.DIAG_DIRECTION_TYPE]

.. py:data:: WALL_THICKNESS_SETTING

   Used as a keyword for wall sizing.

   :type: TypeAlias
   :value: Literal["cellsize", "absolute"]

Module constants
----------------

.. py:data:: COORD_ZERO

    :type: Final[GraphicalCoordinates]
    :value: GraphicalCoordinates(0, 0)

Classes
-------
    
.. autoclass:: GraphicalCoordinates
   :members:

.. autoclass:: GraphicalPath
   :members:

.. autoclass:: OrientedLineSegment
   :members:

.. autoclass:: WallFace
   :members:

.. autoclass:: WallFollowerSVGData
   :members:

.. autoclass:: WallTracker
   :members:

