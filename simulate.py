"""
Interactive Airfoil Flow Simulator
Drag airfoils and watch flow update in real-time with particles!
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle
from matplotlib.widgets import Slider
from matplotlib.animation import FuncAnimation
from interactive1 import flow_around_cylinder

class FlowSimulator:
    """Interactive flow simulator with draggable airfoils"""
    
    def __init__(self, x_range=(-5, 5), y_range=(-5, 5), grid_points=40):
        """Initialize simulator"""
        # Grid setup
        x = np.linspace(x_range[0], x_range[1], grid_points)
        y = np.linspace(y_range[0], y_range[1], grid_points)
        self.X, self.Y = np.meshgrid(x, y)
        
        # Flow parameters
        self.U_inf = 10.0  # Freestream velocity
        
        # Airfoil obstacles
        self.obstacles = [
            {'x': -2.0, 'y': 0.5, 'naca': '2412', 'chord': 2.0, 'angle': 5},
        ]
        
        # Interaction state
        self.dragging = False
        self.drag_obstacle = None
        self.drag_offset = (0, 0)
        
        # Create figure
        self.fig, self.ax = plt.subplots(figsize=(14, 8))
        self.fig.canvas.manager.set_window_title('Airfoil Flow Simulator')
        self.fig.subplots_adjust(bottom=0.2)
        
        # Connect mouse events
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_drag)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        
        # Angle of attack slider
        slider_ax = self.fig.add_axes([0.2, 0.08, 0.6, 0.03])
        self.angle_slider = Slider(
            slider_ax, 
            'Angle of Attack (°)', 
            -20,    # Min angle
            20,     # Max angle
            valinit=5,
            valstep=1
        )

        self.angle_slider.on_changed(self.on_angle_change)
        self.selected_obstacle = 0 

        # Chord slider
        chord_ax = self.fig.add_axes([0.2, 0.08, 0.6, 0.03])
        self.chord_slider = Slider(
            chord_ax, 
            'Chord Length (m)', 
            0.5,    # Min chord
            4.0,     # Max chord
            valinit=2.0,
            valstep=0.1
        )

        self.chord_slider.on_changed(self.on_chord_change)
        # Camber slider
        camber_ax = self.fig.add_axes([0.2, 0.04, 0.6, 0.03])
        self.camber_slider = Slider(
            camber_ax,
            'Camber (%)',
            0, 9, # NCAA first digit (0-9)
            valinit=2,
            valstep=1
        )
        self.camber_slider.on_changed(self.on_camber_change)
        
        # Particle system
        self.particles = []
        self.num_particles = 50
        self.particle_lifetime = 100
        self.show_particles = True
        self.animation = None
        
        self.spawn_particles()
        
        # Initialize flow field
        self.recalculate_flow() 
    
    def generate_airfoil_coords(self, naca='0012', chord=2.0, num_points=100):
        """
        Generate NACA 4-digit airfoil coordinates
        Returns x, y arrays
        """
        m = int(naca[0]) / 100.0  # max camber
        p = int(naca[1]) / 10.0   # position of max camber
        t = int(naca[2:4]) / 100.0  # thickness
        
        # Cosine spacing for better resolution
        beta = np.linspace(0, np.pi, num_points//2)
        x = chord * (1 - np.cos(beta)) / 2
        
        # Thickness distribution
        yt = 5 * t * chord * (
            0.2969 * np.sqrt(x/chord) -
            0.1260 * (x/chord) -
            0.3516 * (x/chord)**2 +
            0.2843 * (x/chord)**3 -
            0.1015 * (x/chord)**4
        )
        
        # Camber line
        if m == 0:
            # Symmetric airfoil
            xu = x
            yu = yt
            xl = x
            yl = -yt
        else:
            # Cambered airfoil
            yc = np.where(x < p*chord,
                         m * (x/(p**2)) * (2*p - x/chord),
                         m * ((chord-x)/((1-p)**2)) * (1 + x/chord - 2*p))
            
            xu = x
            yu = yc + yt
            xl = x
            yl = yc - yt
        
        # Combine upper and lower surfaces
        x_airfoil = np.concatenate([xu, xl[::-1]])
        y_airfoil = np.concatenate([yu, yl[::-1]])
        
        # Center at origin
        x_airfoil -= chord/2
        
        return x_airfoil, y_airfoil
    
    def get_airfoil_coords(self, obs):
        """Get rotated and translated airfoil coordinates"""
        # Generate base airfoil
        x, y = self.generate_airfoil_coords(obs['naca'], obs['chord'])
        
        # Rotate by angle of attack
        angle_rad = np.deg2rad(obs['angle'])
        x_rot = x * np.cos(angle_rad) - y * np.sin(angle_rad)
        y_rot = x * np.sin(angle_rad) + y * np.cos(angle_rad)
        
        # Translate to position
        x_final = x_rot + obs['x']
        y_final = y_rot + obs['y']
        
        return np.column_stack([x_final, y_final])
    
    def get_airfoil_mask(self, obs):
        """Create mask for points inside airfoil (approximate with bounding ellipse)"""
        coords = self.get_airfoil_coords(obs)
        
        # Get bounding box
        x_min, x_max = coords[:, 0].min(), coords[:, 0].max()
        y_min, y_max = coords[:, 1].min(), coords[:, 1].max()
        
        # Create elliptical mask centered on airfoil
        X_rel = self.X - obs['x']
        Y_rel = self.Y - obs['y']
        
        # Rotate to airfoil frame
        angle_rad = np.deg2rad(obs['angle'])
        X_rot = X_rel * np.cos(-angle_rad) - Y_rel * np.sin(-angle_rad)
        Y_rot = X_rel * np.sin(-angle_rad) + Y_rel * np.cos(-angle_rad)
        
        # Ellipse parameters (chord length and max thickness)
        a = obs['chord'] / 2
        b = obs['chord'] * 0.12  # Approximate max thickness
        
        # Elliptical mask
        mask = (X_rot**2 / a**2 + Y_rot**2 / b**2) <= 1.0
        
        return mask
    
    def recalculate_flow(self):
        """Recalculate velocity field for airfoils"""
        # Start with uniform flow
        U = np.ones_like(self.X) * self.U_inf
        V = np.zeros_like(self.Y)
        
        combined_mask = np.zeros_like(self.X, dtype=bool)
        
        for obs in self.obstacles:
            # Use circular flow approximation centered on airfoil
            # (Good enough for visualization - not aerodynamically accurate)
            radius_equiv = obs['chord'] / 2  # Equivalent circle radius
            
            U_obs, V_obs, _ = flow_around_cylinder(
                self.X, self.Y,
                obs['x'], obs['y'],
                radius_equiv,
                self.U_inf
            )
            
            # Add perturbation
            U += (U_obs - self.U_inf)
            V += V_obs
            
            # Mask actual airfoil shape
            mask = self.get_airfoil_mask(obs)
            combined_mask = combined_mask | mask
        
        # Mask inside all airfoils
        U[combined_mask] = np.nan
        V[combined_mask] = np.nan
        
        # Store for particles
        self.U_current = U
        self.V_current = V
    
    def spawn_particles(self):
        """Create initial particles on left side"""
        self.particles = []
        x_min = self.X.min()
        y_min = self.Y.min()
        y_max = self.Y.max()
        
        for i in range(self.num_particles):
            particle = {
                'x': x_min + 0.5,
                'y': np.random.uniform(y_min, y_max),
                'age': np.random.randint(0, self.particle_lifetime),
                'trail': []
            }
            self.particles.append(particle)
    
    def update_particles(self):
        """Move particles based on velocity field"""
        dt = 0.05
        
        for particle in self.particles:
            px, py = particle['x'], particle['y']
            
            try:
                x_vals = self.X[0, :]
                y_vals = self.Y[:, 0]
                
                i = np.argmin(np.abs(y_vals - py))
                j = np.argmin(np.abs(x_vals - px))
                
                u = self.U_current[i, j]
                v = self.V_current[i, j]
                
                if np.isnan(u) or np.isnan(v):
                    particle['age'] = self.particle_lifetime
                    continue
                
                particle['x'] += u * dt
                particle['y'] += v * dt
                
                particle['trail'].append((px, py))
                if len(particle['trail']) > 10:
                    particle['trail'].pop(0)
                
                particle['age'] += 1
                
            except:
                particle['age'] = self.particle_lifetime
        
        # Respawn old particles
        x_min = self.X.min()
        y_min = self.Y.min()
        y_max = self.Y.max()
        
        for particle in self.particles:
            if particle['age'] >= self.particle_lifetime or \
               particle['x'] > self.X.max() or \
               particle['x'] < x_min:
                particle['x'] = x_min + 0.5
                particle['y'] = np.random.uniform(y_min, y_max)
                particle['age'] = 0
                particle['trail'] = []
    
    def draw_particles(self):
        """Draw particles and trails"""
        if not self.show_particles:
            return
        
        for particle in self.particles:
            if len(particle['trail']) > 1:
                trail_x = [p[0] for p in particle['trail']]
                trail_y = [p[1] for p in particle['trail']]
                self.ax.plot(trail_x, trail_y,
                           color='yellow', alpha=0.3, linewidth=1)
            
            self.ax.plot(particle['x'], particle['y'],
                       'o', color='cyan', markersize=4,
                       markeredgecolor='blue', markeredgewidth=0.5)
    
    def on_click(self, event):
        """Handle mouse click on airfoil"""
        if event.inaxes != self.ax:
            return
        
        click_x = event.xdata
        click_y = event.ydata
        
        for i, obs in enumerate(self.obstacles):
            coords = self.get_airfoil_coords(obs)
            x_min, x_max = coords[:, 0].min(), coords[:, 0].max()
            y_min, y_max = coords[:, 1].min(), coords[:, 1].max()
            
            # Simple bounding box check
            if (x_min <= click_x <= x_max and y_min <= click_y <= y_max):
                self.dragging = True
                self.drag_obstacle = i
                self.selected_obstacle = i  # Update slider target
                self.drag_offset = (click_x - obs['x'], click_y - obs['y'])
                
                # Update slider to show current angle
                self.angle_slider.set_val(obs['angle'])
                
                print(f"Grabbed NACA {obs['naca']} at α={obs['angle']}°")
                break
    
    def on_drag(self, event):
        """Handle dragging airfoil"""
        if not self.dragging:
            return
        
        if event.inaxes != self.ax:
            return
        
        mouse_x = event.xdata
        mouse_y = event.ydata
        
        new_x = mouse_x - self.drag_offset[0]
        new_y = mouse_y - self.drag_offset[1]
        
        self.obstacles[self.drag_obstacle]['x'] = new_x
        self.obstacles[self.drag_obstacle]['y'] = new_y
        
        self.recalculate_flow()
        
        print(f"Dragging to ({new_x:.2f}, {new_y:.2f})", end='\r')
    
    def on_release(self, event):
        """Handle mouse release"""
        if self.dragging:
            print(f"\nReleased airfoil {self.drag_obstacle}")
            self.dragging = False
            self.drag_obstacle = None
    
    def on_angle_change(self, val):
        """Update angle of attack from slider"""
        self.obstacles[self.selected_obstacle]['angle'] = val
        self.recalculate_flow()
    
    def on_chord_change(self, val):
        self.obstacles[0]['chord'] = val
        self.recalculate_flow()

    def on_camber_change(self,val):
        old_naca = self.obstacles[0]['naca']
        new_naca = f"{int(val)}{old_naca[1:]}" # Update NACA code to refelect new chord length
        self.obstacles[0]['naca'] = new_naca
        self.recalculate_flow()
    
    def animate(self, frame):
        """Animation loop"""
        self.update_particles()
        self.ax.clear()
        
        speed = np.sqrt(self.U_current**2 + self.V_current**2)
        
        # Draw streamlines
        self.ax.streamplot(self.X, self.Y, self.U_current, self.V_current,
                          density=1.5, linewidth=1.5,
                          color=speed, cmap='viridis', arrowsize=1.2)
        
        # Draw airfoils
        for i, obs in enumerate(self.obstacles):
            coords = self.get_airfoil_coords(obs)
            
            # Color selected airfoil differently
            if i == self.selected_obstacle:
                color = 'orange'
            else:
                color = 'red'
            
            poly = Polygon(coords, facecolor=color, alpha=0.8,
                          edgecolor='darkred', linewidth=2, zorder=10)
            self.ax.add_patch(poly)
            
            # Label airfoil
            self.ax.text(obs['x'], obs['y'], 
                        f"NACA {obs['naca']}\nα={obs['angle']}°",
                        ha='center', va='center', fontsize=8,
                        color='white', weight='bold', zorder=11)
        
        # Draw particles
        self.draw_particles()

        # Formatting
        self.ax.set_xlabel('X position (m)', fontsize=12)
        self.ax.set_ylabel('Y position (m)', fontsize=12)
        self.ax.set_title('interactive flow sim v.2 w/ airfoils',
                         fontsize=14, fontweight='bold')
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.3)
        self.ax.set_xlim(self.X.min(), self.X.max())
        self.ax.set_ylim(self.Y.min(), self.Y.max())
        
        return []
    
    def run(self):
        """Start the simulator"""
        self.animation = FuncAnimation(
            self.fig,
            self.animate,
            interval=33,  # ~30 fps
            blit=False
        )
        
        plt.show()
        print("\n=== Airfoil Flow Simulator ===")
        print("• Click and drag airfoils to move them")
        print("• Use 'Angle of Attack' slider to rotate")
        print("• Use 'Flow Speed' slider to change velocity")
        print("• Orange airfoil is selected")
        print("• Close window to exit")