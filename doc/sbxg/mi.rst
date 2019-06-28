Machine Interface
===============================================================================

Some commands or python API that SBXG provides expose a **machine interface**,
which means formatted data that a script can easily takes as input.

Contents of the library
-------------------------------------------------------------------------------

As explained in :doc:`/sbxg/how_to_use`, the ``sbxg show`` command accepts the
``--mi`` argument, that returns a JSON-formatted string containing the contents
of the library. This paragraph details the format of these data.

The top-level dictionary contains a set of keys that are all lists of two kinds
of objects, that we name here ``Item`` and ``TypedItem``. A list of objects of
type ``T`` will be noted ``list<T>``.

+----------------+---------------------+---------------------------------+
| Top-Level Keys | Type                | Description                     |
+================+=====================+=================================+
| sources        | ``list<TypedItem>`` | List of the sources             |
| toolchains     | ``list<Item>``      | List of the toolchains          |
| configurations | ``list<TypedItem>`` | List of the Kconfig files       |
| boards         | ``list<Item>``      | List of the available boards    |
| bootscripts    | ``list<Item>``      | List of the boot scripts        |
| images         | ``list<Item>``      | List of the images descriptions |
+----------------+---------------------+---------------------------------+

We now describe the ``Item`` and ``TypedItem`` objects:

+---------------+------------+------------------------------------------+
| ``Item`` Keys | Type       | Description                              |
+===============+============+==========================================+
| name          | ``string`` | Name of the item (e.g. value to be used) |
| path          | ``string`` | Absolute path to the associated file     |
+---------------+---------------------+---------------------------------+

+--------------------+------------+--------------------------------------------+
| ``TypedItem`` Keys | Type       | Description                                |
+====================+============+============================================+
| name               | ``string`` | Name of the item (e.g. value to be used)   |
| path               | ``string`` | Absolute path to the associated file       |
| type               | ``string`` | Type of the item (e.g. linux, xen, u-boot) |
+--------------------+---------------------+-----------------------------------+
