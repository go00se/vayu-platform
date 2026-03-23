"""
The main purpose of this file is to utilize the interactive component of matplot lib

MOCKUP
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.widgets import Slider
from matplotlib.animation import FuncAnimation
from interactive1 import flow_around_cylinder

class FlowSimulator:

    def __init__(self, x_range=(-5, 5), y_range=(-5, 5), grid_points=80):
        """
        Going to Initialize simulator
        
        Parameters:
        -----------
        x_range : tuple
            (min, max) for x-axis
        y_range : tuple
            (min, max) for y-axis
        grid_points : int
            Number of grid points (higher = smoother but slower)
        """
        # Grid setup
        x = np.linspace(x_range[0], x_range[1], grid_points)
        y = np.linspace(y_range[0], y_range[1], grid_points)
        self.X, self.Y = np.meshgrid(x, y)
        
        # Flow parameters
        self.U_inf = 10.0  # Freestream velocity
        

        # CHANGE NUMBER OF OBJECTS HERE
        self.obstacles = [
            {'x': -2.0, 'y': 0.0, 'radius': 0.5},
            {'x': 2.0, 'y': 0.0, 'radius': 0.7},
            {'x': 0.0, 'y': 1.5, 'radius': 0.4},
        ]
        
        # Interaction state
        self.dragging = False
        self.drag_obstacle = None  # Which obstacle we're dragging
        self.drag_offset = (0, 0)  # Offset from obstacle center to click point
        
        # Create figure
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        self.fig.canvas.manager.set_window_title('Interactive Flow Simulator')
        
        # Connect mouse events
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_drag)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        
        # SLIDER CODE
        # Initial plot
        self.recalculate_flow()

                # Make room for slider at bottom
        self.fig.subplots_adjust(bottom=0.15)
        
        # Create slider axis
        slider_ax = self.fig.add_axes([0.2, 0.05, 0.6, 0.03])
        self.radius_slider = Slider(
            slider_ax, 
            'Radius', 
            0.1,    # Min radius
            2.0,    # Max radius
            valinit=0.5,  # Initial value
            valstep=0.1
        )
        
        # Connect slider to function
        self.radius_slider.on_changed(self.on_radius_change)
        
        # Track which obstacle to resize (first one by default)
        self.selected_obstacle = 1

        #PARTICLE CODE
        self.particles = []
        self.num_particles = 50
        self.particle_lifetime = 100
        self.show_particles = True
        self.animation = None
        

        self.spawn_particles()

        #particles is a list storing all particle postions (not sure why we have this btw)
        #num_particles is the # of particles are showing
        #particle_lifetime is how long the particles are going to last
        #and then we create the particles
        """
                                What this does:
                            - Sets up grid for calculations
                            - Stores list of obstacles (starts with one cylinder)
                            - Tracks dragging state (are we currently dragging? which obstacle?)
                            - Connects mouse events to functions (we'll write these next)
                            - Creates the plot window

                            Variables:
                            - Self.dragging: True when user is dragging something
                            - Self.drag_obstacle: Which obstacle is being dragged (None if not dragging)
                            - self.drag_offset: How far from the center of the obstacle the click was (to keep it from jumping)
        """

    def on_click(self, event):
        """
        Handles mouse clicks
        """

        if event.inaxes != self.ax:
            return

        click_x = event.xdata
        click_y = event.ydata

        for i, obs in enumerate(self.obstacles):
            distance = np.sqrt((click_x - obs['x'])**2 + (click_y - obs['y'])**2)

            if distance < obs ['radius']:
                self.dragging = True
                self.drag_obstacle = i
                self.drag_offset = (click_x - obs['x'], click_y - obs['y'])
                print(f"Grabbed obstacle {i} at ({obs['x']:.2f}, {obs['y']:.2f})")
                break

    def on_drag(self, event):
        # Only do something if we're actively dragging
        if not self.dragging:
            return
        
        # Ignore if mouse leaves plot area
        if event.inaxes != self.ax:
            return
        
        # Update obstacle position
        mouse_x = event.xdata
        mouse_y = event.ydata
        
        # Subtract offset to get actual obstacle position
        new_x = mouse_x - self.drag_offset[0]
        new_y = mouse_y - self.drag_offset[1]
        
        # Update obstacle
        
        self.obstacles[self.drag_obstacle]['x'] = new_x
        self.obstacles[self.drag_obstacle]['y'] = new_y

        self.recalculate_flow()
        
        print(f"Dragging to ({new_x:.2f}, {new_y:.2f})", end='\r')

    


    
    """
        What this does:

    - Sets up grid for calculations
    - Gets current mouse position
    - Subtracts the offset we stored earlier
    - Updates obstacle position in the list
    - Calls update_flow() to recalculate and redraw
    - end='\r' makes print overwrite same line (cleaner console output)

    """

    def on_release(self, event):
        """
        Handle mouse button release - stop dragging
            
        Parameters:
        -----------
        event : matplotlib mouse event
        """
        if self.dragging:
            print(f"\nReleased obstacle {self.drag_obstacle}")
            self.dragging = False
            self.drag_obstacle = None

    def update_flow(self):
        """
        Recalculate flow field and redraw plot
        This is called whenever obstacles move
        """
        # Clear previous plot
        self.ax.clear()
        
        # Start with uniform flow
        U = np.ones_like(self.X) * self.U_inf
        V = np.zeros_like(self.Y)
        
        # Add contribution from each obstacle
        combined_mask = np.zeros_like(self.X, dtype=bool)
        
        for obs in self.obstacles:
            # Calculate flow around this obstacle
            U_obs, V_obs, mask = flow_around_cylinder(
                self.X, self.Y, 
                obs['x'], obs['y'], 
                obs['radius'], 
                self.U_inf
            )
            
            # Subtract uniform flow (it's already in U, V)
            # We only want the PERTURBATION from this obstacle
            U_uniform_local, V_uniform_local = self.U_inf, 0
            U += (U_obs - U_uniform_local)
            V += (V_obs - V_uniform_local)
            
            # Combine masks
            combined_mask = combined_mask | mask
        
        # Mask inside all obstacles
        U[combined_mask] = np.nan
        V[combined_mask] = np.nan
        
        # Calculate speed for coloring
        speed = np.sqrt(U**2 + V**2)
        
        # Plot streamlines
        self.ax.streamplot(self.X, self.Y, U, V,
                          density=1.5,
                          linewidth=1.5,
                          color=speed,
                          cmap='viridis',
                          arrowsize=1.2)
        
        # Draw obstacles
        for obs in self.obstacles:
            circle = Circle((obs['x'], obs['y']), obs['radius'],
                          color='red', alpha=0.7, zorder=10,
                          edgecolor='darkred', linewidth=2)
            self.ax.add_patch(circle)
        
        # Formatting
        self.ax.set_xlabel('X position (m)', fontsize=12)
        self.ax.set_ylabel('Y position (m)', fontsize=12)
        self.ax.set_title('Interactive Flow Simulator - Drag the obstacle!', 
                         fontsize=14, fontweight='bold')
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.3)
        
        # Redraw
        self.fig.canvas.draw_idle()

    """
        What this does:
    - Clears the previous plot
    - Calculates flow from ALL obstacles using superposition
    - Masks velocity inside obstacles (NaN = streamplot ignores)
    - Draws streamlines
    - Draws red circles for obstacles
    - Redraws canvas: self.fig.canvas.draw_idle()

    BY THE WAY ALL THE SUBNOTES ARE WRITTEN BY ME TO GIVE SHORT EXPLANATIONS

    """
    def on_radius_change(self, val):
        """Update selected obstacle radius when slider moves"""
        self.obstacles[self.selected_obstacle]['radius'] = val
        self.recalculate_flow()

    def spawn_particles(self):
        """
        Create intial particles, and each particle has postion, age and trail history
        """
        self.particles = []
        x_min = self.X.min()
        y_min = self.Y.min()
        y_max = self.Y.max()

        for i in range(self.num_particles):
            # WIll spawn along left with y rand. 
            particle = {
                'x': x_min + 0.5,
                'y': np.random .uniform(y_min, y_max),
                'age': np.random.randint(0, self.particle_lifetime),
                'trail': []
            }
            self.particles.append(particle)

        # essentially we have a bunch of particles along left edge, and we are tracking postion age and trail history

    def update_particles(self):
        """
        Moves particles based on current velocity field speed 
        Uses smth called Euler integration: new_position = old_position + velocity
        """
        dt=0.05 # this is whatever a time step is

        for particle in self.particles:
            px, py = particle['x'], particle['y']
            try:
                x_vals = self.X[0,:]
                y_vals = self.Y[:,0]

                i = np.argmin(np.abs(y_vals - py))
                j= np.argmin(np.abs(x_vals - px))

                u = self.U_current[i,j]
                v= self.V_current[i,j]

                #the following operation is to skip if inside obstacle (velocity is NaN)
                if np.isnan(u) or np.isnan(v):
                    particle['age']= self.particle_lifetime
                    continue

                particle['x'] += u * dt
                particle['y'] += v * dt

                particle['trail'].append((px,py))
                if len(particle['trail']) > 10:
                    particle['trail'].pop(0)

                particle ['age'] += 1

            except:
                particle['age'] = self.particle_lifetime 
        x_min = self.X.min()
        y_min= self.Y.min()
        y_max = self.Y.max()

        for particle in self.particles:
            if particle['age'] >= self.particle_lifetime or \
                particle['x'] > self.X.max() or \
                particle['x'] < x_min:
                    particle ['x'] = x_min + 0.5
                    particle ['y'] = np.random.uniform(y_min, y_max)
                    particle['age'] = 0
                    particle['trail'] = []


    def draw_particles(self):
        if not self.show_particles:
            return
        
        for particle in self.particles:
            if len(particle['trail']) > 1:
                trail_x = [p[0] for p in particle['trail']]
                trail_y = [p[1] for p in particle['trail']]
                self.ax.plot(trail_x, trail_y,
                                            color = 'yellow', alpha=0.3, linewidth=1)
            self.ax.plot(particle['x'], particle['y'], 'o', color = 'cyan', markersize=4, markeredgecolor='blue', markeredgewidth=0.5)
    def animate(self, frame):
        self.update_particles()
        self.ax.clear()
        speed = np.sqrt(self.U_current**2 + self.V_current**2)
        self.ax.streamplot(self.X, self.Y, self.U_current, self.V_current, density=1.5, linewidth=1.5, color=speed, cmap='viridis', arrowsize=1.2)
        for obs in self.obstacles:

            circle = Circle((obs['x'], obs['y']), obs['radius'],
                          color='red', alpha=0.7, zorder=10,
                          edgecolor='darkred', linewidth=2)
            self.ax.add_patch(circle)
        
        self.draw_particles()

        self.ax.set_xlabel('X position (m)', fontsize=12)
        self.ax.set_ylabel('Y position (m)', fontsize=12)
        self.ax.set_title('Interactive Sim, V.1 w/ particles', 
                         fontsize=14, fontweight='bold')
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.3)

        return[]

    def recalculate_flow(self):
        U= np.ones_like(self.X) * self.U_inf
        V= np.zeros_like(self.Y)

        combined_mask = np.zeros_like(self.X, dtype=bool)

        for obs in self.obstacles:
            U_obs, V_obs, mask = flow_around_cylinder(
                self.X, self.Y,
                obs['x'], obs['y'],
                obs['radius'],
                self.U_inf
            )

            U_uniform_local, V_uniform_local = self.U_inf, 0
            U += (U_obs - U_uniform_local)
            V += (V_obs - V_uniform_local)

            combined_mask = combined_mask | mask

        U[combined_mask] = np.nan
        V[combined_mask] = np.nan

        self.U_current = U
        self.V_current = V   
    
    def run(self):
        """
        Start the simulator
        Call this to display the interactive window
        """

        self.animation = FuncAnimation(
            self.fig,
            self.animate,
            interval=33,
            blit=False,
            cache_frame_data=False
        )

        plt.show()
        print("\n=== Interactive Flow Simulator ===")
        print("Click and drag the red obstacle!")
        print("Close window to exit.")

    # Basically just shows the plot and prints instructions to console.
    """
    The Current Slider only impacts the first obstacle, I have just added particles to the simulation, no clue if it will work or not.
    """