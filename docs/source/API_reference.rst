=============
API Reference
=============


.. toctree::
   :maxdepth: 2
   :caption: Contents:

``maze``: Core functionality
=============================================================

.. automodule:: mazeing.maze

.. py:data:: DIRECTION_TYPE

   The four main cardinal directions.

   :type: TypeAlias
   :value: Literal["north", "south", "east", "west"]

.. py:data:: DIAG_DIRECTION_TYPE

   Pairs of cardinal directions (used to represent intercardinal directions, e.g. northeast as ``("north", "east")``).

   :type: TypeAlias
   :value: tuple[DIRECTION_TYPE, DIRECTION_TYPE]

.. autoclass:: AdjacencyInfo
   :members:

.. autoclass:: Maze
   :members:

.. autoclass:: MazeCell
   :members:

.. autoclass:: MazeConstructor
   :members:

.. autoclass:: MazeExit
   :members:

.. autoclass:: MazeWorker
   :members:

.. autoclass:: Position
   :members:

.. autoclass:: WallInfo
   :members:

.. autofunction:: make_maze
