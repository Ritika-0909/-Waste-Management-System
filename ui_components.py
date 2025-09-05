# ui_components.py
import streamlit as st
import pandas as pd
import networkx as nx
from route_calculator import get_optimal_route, get_alternative_routes

DEFAULT_START_NODE = "Dehradun Railway Station"
DEFAULT_END_NODE = "Mussorie"

def render_sidebar(all_locations_sorted):
    """Renders the sidebar controls and returns selected values."""
    st.header("🗺 Map Controls")

    start_default_idx = 0
    if DEFAULT_START_NODE in all_locations_sorted:
        start_default_idx = all_locations_sorted.index(DEFAULT_START_NODE)

    end_default_idx = 5
    if DEFAULT_END_NODE in all_locations_sorted:
        end_default_idx = all_locations_sorted.index(DEFAULT_END_NODE)
    elif len(all_locations_sorted) > 5:
        end_default_idx = 5
    elif all_locations_sorted:
        end_default_idx = len(all_locations_sorted) -1


    start_point = st.selectbox("Start Point (Depot)", all_locations_sorted, index=start_default_idx)
    end_point = st.selectbox("End Point (Destination)", all_locations_sorted, index=end_default_idx)

    st.markdown("---")
    st.header("🚛 Route Options")
    num_alternatives = st.slider("Number of Alternative Routes", 0, 3, 1)
    return start_point, end_point, num_alternatives

def render_route_details_column(G, start_point, end_point, num_alternatives):
    """Renders the route details column and returns calculated path data."""
    st.header("Route Details")
    opt_path_data = {"path": [], "distance": float('inf')}
    alt_paths_data = []

    if not G.has_node(start_point) or not G.has_node(end_point):
        st.error(f"Selected start ('{start_point}') or end ('{end_point}') point is invalid. Please choose from the list.")
        return opt_path_data, alt_paths_data

    if nx.has_path(G, start_point, end_point):
        optimal_path, optimal_distance = get_optimal_route(G, start_point, end_point)
        if optimal_path:
            opt_path_data = {"path": optimal_path, "distance": optimal_distance}
            st.subheader(f"Optimal Route: {optimal_distance:.1f} km")
            st.write(" → ".join(optimal_path))

            alt_paths_data = get_alternative_routes(G, start_point, end_point, num_alternatives)
            for i, alt in enumerate(alt_paths_data):
                st.subheader(f"Alternative {i+1}: {alt['distance']:.1f} km")
                st.write(" → ".join(alt['path']))

            st.markdown("---")
            st.subheader("Route Metrics")
            metric_col1, metric_col2 = st.columns(2)
            metric_col1.metric("Optimal Distance", f"{optimal_distance:.1f} km")
            metric_col2.metric("Est. Optimal Time", f"{(optimal_distance * 2):.0f} min") # Assumes 30km/hr avg speed
        else:
            st.error(f"No path exists between '{start_point}' and '{end_point}'.")
    else:
        st.error(f"No path exists between '{start_point}' and '{end_point}'.")

    return opt_path_data, alt_paths_data


def render_analytics_tabs(G, roads_data):
    """Renders the analytics tabs."""
    st.markdown("---")
    st.header("System Analytics")
    tab1, tab2, tab3 = st.tabs(["Distance Matrix", "Bin Status", "Road Network"])

    with tab1:
        st.subheader("Distance Between All Locations (km)")
        if G.number_of_nodes() > 0:
            try:
                dist_matrix = nx.floyd_warshall_numpy(G, weight='weight')
                dist_df = pd.DataFrame(dist_matrix, index=list(G.nodes), columns=list(G.nodes))
                st.dataframe(dist_df.style.format("{:.1f}").background_gradient(cmap='coolwarm', axis=None))
            except Exception as e:
                st.error(f"Could not compute distance matrix: {e}")
        else:
            st.info("Graph is empty. No distance matrix to display.")

    with tab2:
        st.subheader("Bin Fill Levels")
        bins_info = []
        for node, data in G.nodes(data=True):
            if data.get('type') == 'bin':
                fill_level = data.get('fill_level', 0)
                status = "🟢 Low" if fill_level < 0.5 else "🟡 Medium" if fill_level < 0.8 else "🔴 High"
                bins_info.append({"Bin": node, "Fill Level": fill_level, "Status": status})

        if bins_info:
            status_df = pd.DataFrame(bins_info)
            st.dataframe(status_df.sort_values("Fill Level", ascending=False), use_container_width=True)
        else:
            st.info("No bins found in the current data.")

    with tab3:
        st.subheader("Road Network Analysis")
        if roads_data and len(roads_data) > 0:
            total_dist = sum(d[2] for d in roads_data)
            num_connections = len(roads_data)
            avg_len = total_dist / num_connections if num_connections > 0 else 0
            st.write(f"Total Road Length in Network: {total_dist:.1f} km")
            st.write(f"Number of Road Connections: {num_connections}")
            st.write(f"Average Road Segment Length: {avg_len:.1f} km")
            st.write(f"Number of Locations (Nodes): {G.number_of_nodes()}")
            st.write(f"Graph Density: {nx.density(G):.3f}" if G.number_of_nodes() > 1 else "N/A")
        else:
            st.info("No road data available.")

def render_about_section():
    """Renders the 'About' section for the project."""
    st.markdown("---")
    with st.expander("ℹ About This Project & Team", expanded=False):
        st.markdown("""
        ### What This Project Does
        The "Dehradun & Area Waste Collection Route Optimizer" is an interactive tool designed to:
        - Visualize key locations (waste bins, depot) in and around Dehradun.
        - Calculate and display the shortest (optimal) collection route between a selected start (depot) and end point.
        - Offer alternative routes for flexibility in planning.
        - Provide system analytics, including a distance matrix between all locations, current bin fill levels, and road network statistics.

        Its primary aim is to assist in logistical planning for efficient waste management.

        ### Technologies Used
        - **Python** (core programming language)
        - **Streamlit** (interactive UI and dashboards)
        - **NetworkX** (graph algorithms for shortest path)
        - **Pandas** (data handling and analytics)
        - **NumPy** (matrix calculations for distance)
        """)
