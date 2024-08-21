==========
Trace Manager
==========

The trace manager package is responsible for managing diverse trace extraction strategies. Any additional trace extraction strategies are to be implemented in the trace manager package by extending the ``TraceManager`` base class and implementing its functions.

Class Diagram
^^^^^^^^^^^^

.. image:: TraceManager_ClassDiagram.png

Extraction Strategies
^^^^^^

Custom Latency Extractor
-----------

This extractor requires the latency data in the following format:

.. code-block:: none

    1.json
    2.json
    3.json
    ...

where ``1.json`` represents the latency data of packets from node ``1``. The json format is as follows:

.. code-block:: none

    [
        {
            2: float,
            3: float,
            ...
            n: float
        },
        {
            2: float,
            3: float,
            ....,
            n: float
        }
    ]

Here this is format in ``1.json``. Each object in the array signifies the result in a timestep. Also the key, value in each object signify the destination node and the latency value from node ``1``.



Package
^^^^^^^

.. toctree::
    :maxdepth: 2

    ../src.trace_manager.rst