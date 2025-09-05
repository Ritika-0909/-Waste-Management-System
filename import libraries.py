import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
import pandas as pd
from matplotlib.patches import Circle, Rectangle
from PIL import Image

# Initialize Streamlit
st.set_page_config(layout="wide")
st.title("🗺 Dehradun & Area Waste Collection Route Optimizer")


# --- DATA GENERATION FUNCTIONS ---

def generate_dehradun_layout():
    """Defines a large, static set of locations in and around Dehradun."""
    # (x, y, fill_level)
    locations = {
        # Core Dehradun
        "Forest Research Institute": (200, 450, 0.4), "Indian Military Academy": (150, 250, 0.6),
        "Doon School": (350, 400, 0.7), "Tapkeshwar Mandir": (320, 650, 0.3),
        "Dehradun Railway Station": (550, 100, 0.0), "Clock Tower": (500, 480, 0.9),
        "Gandhi Park": (550, 450, 0.5), "Paltan Bazaar": (580, 350, 0.8),
        "Robber's Cave": (650, 850, 0.4), "Max Super Speciality Hospital": (750, 780, 0.9),
        "Secretariat (Sachivalaya)": (850, 550, 0.6), "ISBT Dehradun": (450, 50, 0.8),
        "Graphic Era University": (350, 100, 0.7), "IT Park": (650, 150, 0.6), "Kandoli": (880, 650, 0.5),
        # New Locations
        "Mussorie": (600, 950, 0.3), "Landour": (630, 980, 0.2), "Chakrata": (50, 900, 0.1),
        "Rajpur": (620, 750, 0.6), "Nagthat": (200, 800, 0.2), "Jolly Grant Airport": (900, 50, 0.8),
        "Bhaniyawala": (950, 100, 0.5), "Miyanwala": (850, 150, 0.7), "Lachhiwala": (800, 120, 0.4),
        "Thano": (850, 250, 0.2), "Asarori": (100, 50, 0.5), "Sahaspur": (100, 400, 0.4),
        "Horawala": (50, 200, 0.3), "Maldevta": (800, 500, 0.3), "Banjarawala": (400, 200, 0.9),
        "Jhanda Mohalla": (500, 250, 0.8), "Mothrowala": (550, 200, 0.7), "Badripur": (700, 250, 0.6),
    }
    return locations

def generate_dehradun_roads(locations):
    """Defines a static road network with distances scaled to represent kilometers."""
    roads = []
    def get_dist_km(p1, p2):
        # Adjusted divisor to create more realistic km distances for the map scale
        return np.sqrt((p2[0]-p1[0])*2 + (p2[1]-p1[1])*2) / 50

    # CORRECTED road_connections list
    road_connections = [
        # Core Dehradun connections
        ("Indian Military Academy", "Forest Research Institute"),
        ("Forest Research Institute", "Doon School"),
        ("Doon School", "Clock Tower"),
        ("Doon School", "Tapkeshwar Mandir"),
        ("Tapkeshwar Mandir", "Clock Tower"),
        ("Clock Tower", "Gandhi Park"),
        ("Clock Tower", "Max Super Speciality Hospital"),
        ("Max Super Speciality Hospital", "Robber's Cave"),
        ("Dehradun Railway Station", "Paltan Bazaar"),
        ("Paltan Bazaar", "Clock Tower"),
        ("Dehradun Railway Station", "ISBT Dehradun"),
        ("Dehradun Railway Station", "IT Park"),
        ("ISBT Dehradun", "Graphic Era University"),
        ("IT Park", "Secretariat (Sachivalaya)"),
        ("Secretariat (Sachivalaya)", "Kandoli"), # <-- THIS LINE IS NOW FIXED

        # North connections
        ("Kandoli", "Rajpur"),
        ("Rajpur", "Clock Tower"),
        ("Mussorie", "Rajpur"),
        ("Landour", "Mussorie"),
        ("Nagthat", "Tapkeshwar Mandir"),

        # West connections
        ("Chakrata", "Sahaspur"),
        ("Sahaspur", "Forest Research Institute"),
        ("Horawala", "Indian Military Academy"),

        # South-East connections
        ("Miyanwala", "IT Park"),
        ("Lachhiwala", "Miyanwala"),
        ("Bhaniyawala", "Lachhiwala"),
        ("Jolly Grant Airport", "Bhaniyawala"),
        ("Thano", "Jolly Grant Airport"),

        # South-West connections
        ("Asarori", "ISBT Dehradun"),

        # Inner City connections
        ("Banjarawala", "ISBT Dehradun"),
        ("Mothrowala", "Banjarawala"),
        ("Mothrowala", "IT Park"),
        ("Jhanda Mohalla", "Dehradun Railway Station"),
        ("Badripur", "Mothrowala"),

        # East connections
        ("Maldevta", "Secretariat (Sachivalaya)")
    ]

    for start, end in road_connections:
        if start in locations and end in locations:
            dist = get_dist_km(locations[start][:2], locations[end][:2])
            roads.append((start, end, round(dist, 1)))

    return list(set(roads))


def build_graph_from_data(locations, roads):
    G = nx.Graph()
    for name, data in locations.items():
        G.add_node(name, pos=(data[0], data[1]), fill_level=data[2],
                  type="center" if name == "Dehradun Railway Station" else "bin")
    for road in roads:
        G.add_edge(road[0], road[1], weight=road[2])
    return G


def draw_dehradun_map(ax, G, routes, map_image_path):
    """Visualization with map background, km labels, and a highly visible optimal path."""
    try:
        img = Image.open(map_image_path)
        ax.imshow(img, extent=[0, 1000, 0, 1000], aspect='auto')
    except FileNotFoundError:
        ax.set_facecolor('#e0e0e0')

    plt.grid(False)
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    # Draw base roads and add distance labels
    for u, v, data in G.edges(data=True):
        pos_u, pos_v = G.nodes[u]['pos'], G.nodes[v]['pos']
        ax.plot([pos_u[0], pos_v[0]], [pos_u[1], pos_v[1]],
                color='#34495e', linewidth=2, zorder=1, alpha=0.6)
        # Add KM label to each road segment
        mid_x, mid_y = (pos_u[0] + pos_v[0]) / 2, (pos_u[1] + pos_v[1]) / 2
        ax.text(mid_x, mid_y, f"{data['weight']:.1f} km", fontsize=7, color='black', zorder=4,
               bbox=dict(facecolor='white', alpha=0.7, pad=1, edgecolor='none'))

    # Styles for routes
    optimal_style = {'color': '#FF3333', 'linewidth': 7, 'linestyle': '-', 'arrow_headwidth': 35}
    alt_style = {'color': '#00BFFF', 'linewidth': 3.5, 'linestyle': '--', 'arrow_headwidth': 25}

    for i, route in enumerate(routes):
        if len(route["path"]) > 1:
            style = optimal_style if i == 0 else alt_style
            path_edges = list(zip(route["path"], route["path"][1:]))
            segments = [(G.nodes[u]['pos'], G.nodes[v]['pos']) for u, v in path_edges]

            lc = LineCollection(segments, colors=style['color'], linewidths=style['linewidth'],
                                zorder=5, alpha=1.0, linestyle=style['linestyle'])
            ax.add_collection(lc)

            for u, v in path_edges:
                pos_u, pos_v = G.nodes[u]['pos'], G.nodes[v]['pos']
                dx, dy = pos_v[0] - pos_u[0], pos_v[1] - pos_u[1]
                ax.arrow(pos_u[0], pos_u[1], dx*0.8, dy*0.8,
                         head_width=style['arrow_headwidth'], head_length=style['arrow_headwidth']*0.8,
                         fc=style['color'], ec=style['color'], zorder=6, length_includes_head=True)

    # Draw locations
    for node, data in G.nodes(data=True):
        marker_color = '#e74c3c' if data['type'] == 'center' else plt.cm.YlOrRd(data['fill_level'])
        marker_size = 400 if data['type'] == 'center' else 150 + data['fill_level']*200
        marker_shape = '*' if data['type'] == 'center' else 'o'
        ax.scatter(data['pos'][0], data['pos'][1], s=marker_size, marker=marker_shape,
                   color=marker_color, edgecolor='black', linewidth=1.5, zorder=9)
        ax.text(data['pos'][0], data['pos'][1]+25, node, ha='center', va='bottom', fontsize=9,
                zorder=11, bbox=dict(facecolor='white', alpha=0.8, pad=1, edgecolor='none'), weight='bold')

    # Add legend
    legend_elements = [
        plt.Line2D([0], [0], marker='*', color='w', label='Collection Depot', markerfacecolor='#e74c3c', markersize=15),
        plt.Line2D([0], [0], marker='o', color='w', label='Waste Bin', markerfacecolor='#f1c40f', markersize=10),
        plt.Line2D([0], [0], color=optimal_style['color'], lw=5, label='Optimal Route'),
        plt.Line2D([0], [0], color=alt_style['color'], lw=3, linestyle=alt_style['linestyle'], label='Alternative Route')
    ]
    ax.legend(handles=legend_elements, loc='lower left', fontsize=10)


# --- MAIN APP LOGIC ---

if 'G' not in st.session_state:
    st.session_state.locations = generate_dehradun_layout()
    st.session_state.roads = generate_dehradun_roads(st.session_state.locations)
    st.session_state.G = build_graph_from_data(st.session_state.locations, st.session_state.roads)

# Sidebar
with st.sidebar:
    st.header("🗺 Map Controls")
    sorted_locations = sorted(list(st.session_state.G.nodes()))
    start_default = "Dehradun Railway Station"
    end_default = "Mussorie"
    start_index = sorted_locations.index(start_default) if start_default in sorted_locations else 0
    end_index = sorted_locations.index(end_default) if end_default in sorted_locations else 5
    start_point = st.selectbox("Start Point (Depot)", sorted_locations, index=start_index)
    end_point = st.selectbox("End Point (Destination)", sorted_locations, index=end_index)
    st.markdown("---")
    st.header("🚛 Route Options")
    num_alternatives = st.slider("Number of Alternative Routes", 0, 3, 1)

# Main content
col1, col2 = st.columns([1,2])
G = st.session_state.G
opt_path, alt_paths = [], []

with col1:
    st.header("Route Details")
    try:
        if nx.has_path(G, start_point, end_point):
            opt_path = nx.shortest_path(G, start_point, end_point, weight='weight')
            opt_dist = nx.shortest_path_length(G, start_point, end_point, weight='weight')
            st.subheader(f"Optimal Route: {opt_dist:.1f} km")
            st.write(" → ".join(opt_path))

            if num_alternatives > 0:
                path_gen = nx.shortest_simple_paths(G, start_point, end_point, weight='weight')
                for i, path in enumerate(path_gen):
                    if i == 0: continue
                    alt_paths.append({
                        "path": path,
                        "distance": sum(G[path[j]][path[j+1]]['weight'] for j in range(len(path)-1))
                    })
                    if len(alt_paths) >= num_alternatives: break

            for i, alt in enumerate(alt_paths):
                st.subheader(f"Alternative {i+1}: {alt['distance']:.1f} km")
                st.write(" → ".join(alt['path']))

            st.markdown("---")
            st.subheader("Route Metrics")
            metric_col1, metric_col2 = st.columns(2)
            metric_col1.metric("Total Distance", f"{opt_dist:.1f} km")
            metric_col2.metric("Estimated Time", f"{(opt_dist*2):.0f} min")
        else:
            st.error(f"No path exists between '{start_point}' and '{end_point}'.")
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        st.error("Could not find a route.")

with col2:
    st.header("Dehradun Interactive Route Map")
    viz_routes = []
    if opt_path:
        viz_routes.append({"path": opt_path, "distance": opt_dist})
        for alt in alt_paths:
            viz_routes.append(alt)

    fig, ax = plt.subplots(figsize=(12, 12))
    draw_dehradun_map(ax, G, viz_routes, "dehradun_map.jpg")
    st.pyplot(fig)

# Analytics Tabs
st.markdown("---")
st.header("System Analytics")
tab1, tab2, tab3 = st.tabs(["Distance Matrix", "Bin Status", "Road Network"])
with tab1:
    st.subheader("Distance Between All Locations (km)")
    dist_matrix = nx.floyd_warshall_numpy(G, weight='weight')
    dist_df = pd.DataFrame(dist_matrix, index=list(G.nodes), columns=list(G.nodes))
    st.dataframe(dist_df.style.format("{:.1f}").background_gradient(cmap='coolwarm', axis=None))
with tab2:
    st.subheader("Bin Fill Levels")
    bins = [node for node, data in G.nodes(data=True) if data['type'] == 'bin']
    fill_levels = [G.nodes[node]['fill_level'] for node in bins]
    status_df = pd.DataFrame({"Bin": bins, "Fill Level": fill_levels, "Status": ["🟢 Low" if lvl < 0.5 else "🟡 Medium" if lvl < 0.8 else "🔴 High" for lvl in fill_levels]})
    st.dataframe(status_df.sort_values("Fill Level", ascending=False), use_container_width=True)
with tab3:
    st.subheader("Road Network Analysis")
    road_data = st.session_state.roads
    if len(road_data) > 0:
        st.write(f"Total Road Length in Network: {sum(d[2] for d in road_data):.1f} km")
        st.write(f"Number of Road Connections: {len(road_data)}")
        st.write(f"Average Road Segment Length: {sum(d[2] for d in road_data)/len(road_data):.1f} km")