DOPING
========

Project Description
-------------------

.. description-begin-marker-do-not-remove

Doping is a transparent and fully automatic framework that does source-to-source
transformation and runtime compilation for enhancing the vectorisation of scientific
applications. The framework masquerades the overall compilation and execution through
a number of aspects.
First it performs limited source-to-source, compile-time transformation to inject the
code that facilitates dynamic evaluation of loops. During the dynamic evaluation, the
framework delays the execution as much as possible to leverage potential runtime-only
information, which are otherwise, unavailable to the compilers during static analysis.
Once the framework believes that enough information has been collected to facilitate
the vectorisation, it recompiles the ideal candidates (for the time being, these are
loops) and links that to the currently running code.

Although it is possible to know more at runtime, a number of challenges do exist. First,
delayed evaluation may not always pay off. After all, we may not find any candidates
that massively benefits from vectorisation. Secondly, it is always a question, how much
delaying is good. The aim of this framework is to facilitate the research into runtime
vectorisation.

.. description-end-marker-do-not-remove


User's Guide
------------

.. usersguide-begin-marker-do-not-remove

Building instructions
`````````````````````

Doping uses the llvm libclang, which can be installed from your Package manager of
choice. If libclang is installed manually make sure to add `libclang.so` path to
`LD_LIBRARY_PATH`. All other dependencies are embedded or managed by the `pip`
command, you can install them with:

.. code-block:: bash

    pip install -e . 

To build the Doping runtime use:

.. code-block:: bash

    make

If it succeeds the `bin` folder should contains the files: `dope`, `doping.h` and
`libdoping.so`.

The make targets below verify Doping is running correctly and demonstrate a simple example:

.. code-block:: bash

    make test
    make examples
    make quickrun


Usage
`````
To use Doping, first specify the DOPING_ROOT environment variable to point this
repository.

.. code-block:: bash

    export DOPING_ROOT=$PWD

Then prepend a compiler command with the `dope` command:

.. code-block:: bash

    dope [doping_options] -- compiler_command

For example:

.. code-block:: bash

    cd examples/quick_examples/multiplematrixmult/
    dope -- gcc -O2 mm.cc -o mm.exe


Alternatively, you can try intercepting build system compiler invocations with:

.. code-block:: bash

    CC="./doping [doping_options] -- icc" make

Finally, run the produced binary as normal, Doping runtime optimization will
be triggered under-the-hood when a loop can be optimized. Optionally, the
DOPING_VERBOSE environment variable can be set with a verbosity level in
order to print more information about what Doping is doing during the execution
of a program:

.. code-block:: bash

    ./mm.exe 50 10000
    DOPING_VERBOSE=1 ./mm.exe 50 10000

.. usersguide-end-marker-do-not-remove


Developer's Guide
-----------------

.. developersguide-begin-marker-do-not-remove

In addition to the dependencies mentioned on the User's Guide,
developers can install: pytest, pytest-cov, pycodestyle,
Sphinx and sphinx_rtd_theme, this will allow to run the
unit-tests and to build the documentation:

.. code-block:: bash

    pip install -e .[dev]


As Doping is still under development, we don't enforce the development
guidelines in the master branch, but ideally the following guideline
must be followed:

1. Document all new code using pyhton docstring.

2. Make sure all unit tests and integration tests pass by executing:

.. code-block:: bash

    make test

3. Create a unit test for every new code addition, check the code coverage with:

.. code-block:: bash

    pytest --cov-report=term --cov=src/codegen


5. Add the appropriate documentation in the `doc/source` directory and check it generates with:

.. code-block:: bash

    cd doc
    make html


6. Make sure all code passes the pycodestyle format test.

.. code-block:: bash

    pycodestyle src/codegen/*

Note that there are additional dependencies to generate new UML diagram images (Plantuml,
java and graphviz) and Latex documentation(Latex distribution). These should be installed
manually.

Finally, to clean binaries and temporal files you can use:

.. code-block:: bash

    make clean


.. developersguide-end-marker-do-not-remove

Contributors
------------
- Sergi Siso <sergi.siso@stfc.ac.uk>
- Jeyan Thiyagalingam <T.Jeyarajan@liverpool.ac.uk>
