=============
API Reference
=============


.. toctree::
   :maxdepth: 2
   :caption: Contents:

``maze``: Core functionality
=============================================================

.. automodule:: mazeing.maze

TypeAliases
-----------

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
