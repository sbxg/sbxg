Coding Practises
===============================================================================

Coding Style
-------------------------------------------------------------------------------

Hate it or love it, but SBXG shall conform to PEP8_. Docstrings shall conform
to PEP257_. There is currently no strict enforcement of these rules.


Linting
-------------------------------------------------------------------------------

We use `pylint <https://www.pylint.org/>`_ to lint SBXG. It is not run
automatically, because there's nothing worse than seeing that your build fails
because of an extraneous whitespace, or a rightful TODO you added. Use the
linter to help you code, don't bow to it.

To lint, just run the following from the top source directory::

   pylint


Tests
-------------------------------------------------------------------------------

We use `pytest <https://docs.pytest.org>`_ to run SBXG's tests. It is a bit
unusual to test, because it has a lot of interactions with the filesystem,
which makes it not obvious to unit test it.

Also, since the goal of SBXG is to generate a build system, one of the
possiblities to check that the build system was correctly generated is to run
it, and see what happens. That's the simple and obvious method. Problem is that
we build sevaral Linux kernels... which take a lot of time to be downloaded and
built. So, testing the correctness of the generated file is not that trivial
after all. Currently, we run the generated Makefile for a single case that
should cover most of the usecases, but it is not systematically executed.

To run the tests, just run the following from the top source directory::

   pytest


Documentation
-------------------------------------------------------------------------------

Documentation is obviously very important. It's not always clear what to write,
and how it should be written, but we try to figure out as we grow.
Documentation, which is often looked down upon by developers tries to be a
first-class citizen in SBXG. It demands work and dedication, but you'll get
used to it. We use Sphinx_ to manage the documentation.

To build the documentation, run the following from the top source directory::

  make -C doc html


Contributions
-------------------------------------------------------------------------------

.. admonition:: This is currently a mess.
  :class: warning

  TODO.


.. _PEP8: https://www.python.org/dev/peps/pep-0008/
.. _PEP257: https://www.python.org/dev/peps/pep-0257/
.. _Sphinx: http://www.sphinx-doc.org/en/master/index.html
