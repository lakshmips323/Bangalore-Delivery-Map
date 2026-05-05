import streamlit as st
import osmnx as ox
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")

st.title("🚚 Bangalore Delivery Routing Comparison")

GRAPH_FILE = "bangalore_bike_network.graphml"


@st.cache_resource
def load_graph():
    return ox.load_graphml(GRAPH_FILE)


G = load_graph()
nodes, edges = ox.graph_to_gdfs(G)


locations = {
    "Koramangala": (12.9352, 77.6245),
    "Shivajinagar": (12.9867, 77.6056),
    "Richmond Circle": (12.9611, 77.5944),
    "St Josephs College": (12.9596, 77.5993),
    "Whitefield": (12.9698, 77.7499),
    "MG Road": (12.9758, 77.6065),
    "Indiranagar": (12.9716, 77.6412),
    "Electronic City": (12.8456, 77.6603),
    "Hebbal": (13.0358, 77.5970)
}


col1, col2 = st.columns(2)

start = col1.selectbox("From", list(locations.keys()))
end = col2.selectbox("To", list(locations.keys()), index=4)


src = locations[start]
dst = locations[end]


G2 = G.copy()

G2 = ox.add_edge_speeds(G2)
G2 = ox.add_edge_travel_times(G2)


orig = ox.nearest_nodes(G2, src[1], src[0])
dest = ox.nearest_nodes(G2, dst[1], dst[0])


# FASTEST ROUTE
fastest = ox.shortest_path(G2, orig, dest, weight="travel_time")


# DELIVERY ROUTE (avoid highways)
for u, v, k, data in G2.edges(keys=True, data=True):

    highway = data.get("highway", "")

    penalty = 0

    if highway in ["primary", "secondary", "trunk"]:
        penalty = 60

    data["delivery_cost"] = data["travel_time"] + penalty


delivery = ox.shortest_path(G2, orig, dest, weight="delivery_cost")


# Calculate times
fast_time = sum(
    G2[u][v][0]["travel_time"] for u, v in zip(fastest[:-1], fastest[1:])
) / 60

delivery_time = sum(
    G2[u][v][0]["travel_time"] for u, v in zip(delivery[:-1], delivery[1:])
) / 60


st.subheader("Route Time Comparison")

c1, c2 = st.columns(2)

c1.metric("⚡ Fastest Route", f"{fast_time:.2f} minutes")
c2.metric("📦 Delivery Route", f"{delivery_time:.2f} minutes")


st.subheader("Route Map")


m = folium.Map(location=src, zoom_start=12)


# DELIVERY ROUTE FIRST
folium.PolyLine(
    [(nodes.loc[n].geometry.y, nodes.loc[n].geometry.x) for n in delivery],
    color="green",
    weight=5,
    tooltip="Delivery Route"
).add_to(m)


# FASTEST ROUTE ON TOP
folium.PolyLine(
    [(nodes.loc[n].geometry.y, nodes.loc[n].geometry.x) for n in fastest],
    color="red",
    weight=7,
    tooltip="Fastest Route"
).add_to(m)


folium.Marker(src, tooltip="Start").add_to(m)
folium.Marker(dst, tooltip="Destination").add_to(m)


st_folium(m, width=1200, height=650)