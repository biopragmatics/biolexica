Installation
============

The most recent release can be installed from `PyPI
<https://pypi.org/project/biolexica>`_ with uv:

.. code-block:: console

    $ uv pip install biolexica

or with pip:

.. code-block:: console

    $ python3 -m pip install biolexica

Installing from git
-------------------

The most recent code and data can be installed directly from GitHub with uv:

.. code-block:: console

    $ uv --preview pip install git+https://github.com/biopragmatics/biolexica.git

or with pip:

.. code-block:: console

    $ UV_PREVIEW=1 python3 -m pip install git+https://github.com/biopragmatics/biolexica.git

.. note::

    The ``UV_PREVIEW`` environment variable is required to be set until the uv build
    backend becomes a stable feature.

Installing for development
--------------------------

To install in development mode with uv:

.. code-block:: console

    $ git clone git+https://github.com/biopragmatics/biolexica.git
    $cd biolexica
    $ uv --preview pip install -e .

or with pip:

.. code-block:: console

    $ UV_PREVIEW=1 python3 -m pip install -e .
