import numpy as np
import matplotlib.pyplot as plt


def plot_velocity_field(X, Y, U, V, title="Velocity Field"):
    fig, ax = plt.subplots(figsize=(10, 6)) # Using a quiver plot to visualize velocity fields
    ax.quiver(X, Y, U, V, 
              scale=50,      # Controls arrow length (bigger = shorter arrows)
              width=0.003,   # Arrow thickness                                           # Just parameters to make the plot look better
              color='blue',  # Arrow color
              alpha=0.7)


    ax.set_xlabel('X position (m)', fontsize=12)
    ax.set_ylabel('Y position (m)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_aspect('equal')  # Equal scaling on both axes
    ax.grid(True, alpha=0.3)  # Light grid for reference

    plt.tight_layout()
    plt.show()

def plot_streamlines(X, Y, U, V, title="Streamlines"):
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # matplotlib has built-in streamline plotting!
    # density controls how many streamlines (higher = more lines)
    # linewidth controls thickness
    # color can be speed magnitude for prettier plots
    
    speed = np.sqrt(U**2 + V**2)  # Calculate speed at each point
    
    strm = ax.streamplot(X, Y, U, V,
                         density=2,           # Streamline density
                         linewidth=1,         # Line thickness
                         color=speed,         # Color by speed
                         cmap='viridis',      # Color map
                         arrowsize=1.5)       # Arrow size
    
    # Add colorbar showing what colors mean
    cbar = plt.colorbar(strm.lines, ax=ax)
    cbar.set_label('Speed (m/s)', fontsize=12)
    
    ax.set_xlabel('X position (m)', fontsize=12)
    ax.set_ylabel('Y position (m)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
