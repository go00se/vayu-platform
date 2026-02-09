import numpy as np
import sys
sys.path.append('../src')
from visualization import plot_streamlines

# Domain
x = np.linspace(-5, 5, 50)
y = np.linspace(-5, 5, 50)
X, Y = np.meshgrid(x, y)

U1 = np.ones_like(X) * 10.0 
V1 = np.zeros_like(Y)
plot_streamlines(X, Y, U1, V1, title="Uniform test w/ colors and streamlines")

U2 = X / (X**2 + Y**2 + 0.1)  # Radial outward
V2 = Y / (X**2 + Y**2 + 0.1)
plot_streamlines(X, Y, U2, V2, title="Simple radial test")


U3 = -Y / (X**2 + Y**2 + 0.1)  # Circular
V3 = X / (X**2 + Y**2 + 0.1)
plot_streamlines(X, Y, U3, V3, title="Circle flow, but acc its vortex flow")

doublet_strength = 5.0
r_squared = X**2 + Y**2 + 0.1

U4 = 10.0 + doublet_strength * (X**2 - Y**2) / r_squared**2
V4 = doublet_strength * (2 * X * Y) / r_squared**2
plot_streamlines(X, Y, U4, V4, title="Flow around some object")
