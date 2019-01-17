.. _getting-going:

Getting Going
=============


User's Guide
-------------

.. include:: ../../README.rst
  :start-after: usersguide-begin-marker-do-not-remove
  :end-before: usersguide-end-marker-do-not-remove

The 
::

    usage: dope [-h] [-v] [--dose {0,1,2,3}]
                [--optimization {delay_evaluation,compiler_pgo,loop_tiling}]
                [--save-files]
                compiler_command [compiler_command ...]

    positional arguments:
      compiler_command      the command used by the compiler

    optional arguments:
      -h, --help            show this help message and exit
      -v, --verbose         increase output verbosity
      --dose {0,1,2,3}      dose supports the following:
                                0   - Don't inject dynamic optimizations unless
                                      explicitly requested by marking the loops
                                      with '#pragma doping'.
                                1   - (default) Conservatively inject dynamic
                                      optimizations.
                                2   - Aggressively inject dynamic optimizations.
                                3   - Inject dynamic optimizations to all loops
                                      that support them.

      --optimization {delay_evaluation,compiler_pgo,loop_tiling}
                            optimization supports the following:
                                delay_evaluation    - Description. (default)
                                compiler_pgo        - Description.
                                loop_tiling         - Description.

      --save-files          Store Doping intermediate files. Useful for debugging.


Developer's Guide
------------------

.. include:: ../../README.rst
  :start-after: developersguide-begin-marker-do-not-remove
  :end-before: developersguide-end-marker-do-not-remove
