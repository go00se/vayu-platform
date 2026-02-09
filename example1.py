import numpy as np
import sys
sys.path.append('../src')  # Tells Python where to find our code
from visualization import plot_velocity_field
from visualization import plot_streamlines


x_start, x_end = 0, 10 # the range of x values for our grid (in meters)
y_start, y_end = 0, 5  # the range of y values for our grid (in meters)
num_points = 20  # the number of points in each direction (x and y) for our grid

x = np.linspace(x_start, x_end, num_points)
y = np.linspace(y_start, y_end, num_points) # this function basically splits the range of x and y into points that are equally spaced points.

# np.meshgrid creates 2D arrays of all (x,y) combinations
# Basically we gave the graph two axes's and points and now it turns it into a matrice
X, Y = np.meshgrid(x, y)

print(f"Grid shape: {X.shape}")  # Should be (20, 20)
print(f"Total points: {X.size}") # Should be 400

# STEP 3: Define uniform flow velocity

freestream_velocity = 10.0  # meters/second

# U = velocity in x-direction (all points moving right at 10 m/s)
# V = velocity in y-direction (no vertical movement)



print(f"U at point (0,0): {U[0,0]} m/s")  # Should be 10.0
print(f"V at point (0,0): {V[0,0]} m/s")  # Should be 0.0

# STEP 4: Visualize it!
plot_streamlines(X, Y, U, V, title="Uniform Flow Streamlines - Week 1")  


# Jorunal 2 So now that we have vector graphs that show flow, we need to implement actual changes, I am trying to add shapes that you can drag and drop 

