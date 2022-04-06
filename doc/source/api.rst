.. _api:

Developer's API
===============

.. image:: images/uml/classes.png

Rewriter Class
--------------

.. autoclass:: codegen.rewriter.Rewriter
    :members:
    :undoc-members:


AST Related Classes
-------------------

.. autoclass:: codegen.ast.translation_unit.DopingTranslationUnit
    :members:
    :undoc-members:

.. autoclass:: codegen.ast.cursors.DopingCursor
    :members:
    :inherited-members:
    :undoc-members:

.. autoclass:: codegen.ast.cursors.DeclarationCursor
    :members:
    :undoc-members:

.. autoclass:: codegen.ast.cursors.ForCursor
    :members:
    :undoc-members:

Code Transformation Class
-------------------------

.. autoclass:: codegen.transformations.transformation.CodeTransformation
    :members:
    :undoc-members:
