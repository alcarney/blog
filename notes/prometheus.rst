Kubernetes Focused Prometheus Queries
=====================================

Queries
-------

A collection of queries for inspecting data stored in a Prometheus server. Most
of these queries should work in vanilla prometheus however a small number may
contain a few "grafana-isms"

The following variables are used as examples

=============  ===========
Name           Description
=============  ===========
``$interval``  A time interval e.g. ``1m``. ``5m``, ``1h`` etc.
=============  ===========

Nodes
^^^^^

Queries relating to the state of the "physical" hardware that is hosting the
cluster

The following metrics are used in the exmaples

==========================  ===========
Name                        Description
==========================  ===========                     
``node_cpu_seconds_total``  CPU time broken down into ``modes`` e.g. ``idle``, ``system``, ``user``
``node_load1/5/15``         1m, 5m, 15m CPU load averages.
==========================  ===========                     

CPU
"""

CPU Utilisation, broken down by node

.. code-block:: none

   sum(rate(node_cpu_seconds_total{mode!="idle", mode!="iowait"}[$interval])) by (instance)

CPU load times, broken down by node normalised by number of cores

.. code-block:: none

   sum(node_load1) by (instance) / count(node_cpu_seconds_total{mode="system"}) by (instance) * 100

Kubernetes
^^^^^^^^^^

A collection of queries specific to kubernetes instances

Pods
""""

Useful for alerts, this query returns which pods are not ready

.. code-block:: none

   sum(kube_pod_container_status_ready) by (pod) < 1

This returns the number of times a pod has restarted

.. code-block:: none

   kube_pod_container_status_restarts_total

Useful for alerts, this query will return the pods that are waiting
and the reason for the delay

.. code-block:: none

   sum(kube_pod_container_status_waiting_reason) by (pod, reason) > 0

Services
""""""""

A collection of queries for metrics useful for monitoring services

The following metrics will be used as examples

============================  ===========
Name                          Description
============================  ===========
``service_requests``          A counter that counts the number of requests received                     
``service_requests_latency``  A histogram that records the response times for a request                 
``service_info``              A counter that encodes information about the service in the metric labels 
============================  ===========


The number of requests received (usually per second)

.. code-block:: none

   sum(rate(service_requests[$interval]))

The number of internal server errors (5xx responses), again usually per second

.. code-block:: none

   sum(rate(service_requests{code=~"5.*"}[$interval]))

The number of user errors (4xx responses), per second

.. code-block:: none

   sum(rate(service_requests{code=~"4.*"}[$interval]))

Each of the by can be broken down by service (assuming the existence of a
``service`` label in the scraped data) as follows

.. code-block:: none

   sum(rate(fdm_requests[$interval])) by (service)

Request latencies are recorded as a histogram and so we can only collect
aggregate values. As far as I can tell the usual way to do this is to generate
the following datapoints

- 95th/99th percentile
- 50th percentile / median
- average response time

The Xth percentile tells us the upper bound on the amount of time X% requests
are processed in. E.g. if the 95th percentile is 500ms, then 95% of requests are
handled in 500ms or less.

Using these metrics we can get a feel for the distribution of the request times:

- If the median coincides with the mean then we can infer that the response
  times are normally distributed
- If the mean < median then the distribution is skewed towards zero i.e. the
  majority of requests are being processed quicker
- If the mean > median then the distribution is skewed high, i.e. the majority
  of requests take a longer time to be processed.

To generate the Xth percentile

.. code-block:: none

   histogram_quantile(0.X, sum(rate(service_requests_latency_bucket[$interval])) by (le))

.. note:: 

   This will only work if the bucket label is called ``le``

To get the average

.. code-block:: none

   sum(rate(service_requests_latency_sum[$interval])) / sum(rate(service_requests_latency_count[$interval]))

To get a count of the number of services

.. code-block:: none

   count(sum(service_info) by (service))

Assuming the existence of a ``service`` label
