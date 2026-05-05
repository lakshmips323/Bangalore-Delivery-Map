# Data Source

The Bangalore road network is dynamically fetched using OSMnx:

```python
G = ox.graph_from_place("Bangalore, India", network_type="drive")
