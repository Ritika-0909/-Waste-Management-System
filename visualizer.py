# visualizer.py
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from PIL import Image
# from matplotlib.patches import Circle, Rectangle # Not explicitly used

def draw_dehradun_map(ax, G, routes, map_image_path):
    """Visualization with map background, km labels, and a highly visible optimal path."""
    try:
        img = Image.open(map_image_path)
        # Adjust extent if your map image has different dimensions or coordinate system
        ax.imshow(img, extent=[0, 1000, 0, 1000], aspect='auto', zorder=0)
    except FileNotFoundError:
        print(f"Warning: Map image '{map_image_path}' not found. Using plain background.")
        ax.set_facecolor('#e0e0e0') # Light grey background if no map

    plt.grid(False) # Turn off matplotlib grid
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_xticks([])
    ax.set_yticks([])

    # Draw base roads and add distance labels
    for u, v, data in G.edges(data=True):
        pos_u, pos_v = G.nodes[u]['pos'], G.nodes[v]['pos']
        ax.plot([pos_u[0], pos_v[0]], [pos_u[1], pos_v[1]],
                color='#34495e', linewidth=2, zorder=1, alpha=0.6)
        mid_x, mid_y = (pos_u[0] + pos_v[0]) / 2, (pos_u[1] + pos_v[1]) / 2
        ax.text(mid_x, mid_y, f"{data['weight']:.1f} km", fontsize=7, color='black', zorder=4,
               bbox=dict(facecolor='white', alpha=0.7, pad=1, edgecolor='none'))

    # Styles for routes
    optimal_style = {'color': '#FF3333', 'linewidth': 7, 'linestyle': '-', 'arrow_headwidth': 15, 'arrow_headlength': 20}
    alt_style = {'color': '#00BFFF', 'linewidth': 3.5, 'linestyle': '--', 'arrow_headwidth': 10, 'arrow_headlength': 15}

    for i, route_info in enumerate(routes):
        route_path = route_info["path"]
        if len(route_path) > 1:
            style = optimal_style if i == 0 else alt_style
            path_edges = list(zip(route_path, route_path[1:]))
            segments = []
            for u_node, v_node in path_edges:
                if u_node in G.nodes and v_node in G.nodes:
                     segments.append((G.nodes[u_node]['pos'], G.nodes[v_node]['pos']))
                else:
                    print(f"Warning: Node not found in path for drawing: {u_node} or {v_node}")
                    continue
            if not segments: continue

            lc = LineCollection(segments, colors=style['color'], linewidths=style['linewidth'],
                                zorder=5, alpha=1.0, linestyle=style['linestyle'])
            ax.add_collection(lc)

            for u_node, v_node in path_edges:
                if u_node in G.nodes and v_node in G.nodes:
                    pos_u, pos_v = G.nodes[u_node]['pos'], G.nodes[v_node]['pos']
                    dx, dy = pos_v[0] - pos_u[0], pos_v[1] - pos_u[1]
                    if dx == 0 and dy == 0: continue

                    ax.arrow(pos_u[0], pos_u[1], dx * 0.9, dy * 0.9,
                            head_width=style['arrow_headwidth'],
                            head_length=style['arrow_headlength'],
                            fc=style['color'], ec=style['color'], zorder=6,
                            length_includes_head=True, overhang=0.3)

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
        plt.Line2D([0], [0], marker='o', color='w', label='Waste Bin (Fill Level)', markerfacecolor='#f1c40f', markersize=10),
        plt.Line2D([0], [0], color=optimal_style['color'], lw=5, label='Optimal Route'),
        plt.Line2D([0], [0], color=alt_style['color'], lw=3, linestyle=alt_style['linestyle'], label='Alternative Route')
    ]
    ax.legend(handles=legend_elements, loc='lower left', fontsize=10, frameon=True, facecolor='white', framealpha=0.8)
    ax.set_aspect('equal', adjustable='box')