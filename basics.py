import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits import mplot3d

x= np.linspace(-5, 5, 10) # these are two axes of the plot
y=x**3  # here we are taking the x values and cubing them


# plt.plot() just calculates and prepares plot data.


# plt.show() is to display the plot in an interactive window


fig= plt.figure(figsize=(10,5)) # this creates a figure object which is the entire window or page that everything is drawn on.
axes1 = fig.add_axes([0.1,0.1,0.8,0.8]) # this creates a set of axes on the figure. The list [0.1, 0.1, 0.8, 0.8] specifies the position and size of the axes in the figure (left, bottom, width, height).
 

# Alright there is a lot of functionality in terms of 2d plots, such as scatter, bar, histogram, pie etc. but foucs on 3d plots.

fig1=plt.figure(figsize=(10,5)) # figsize is the size of the figure in inches. The first value is the width and the second value is the height.
axes2=fig1.add_axes([0.1,0.1,0.9,0.9], projection='3d') # this creates a set of axes on the figure. The list [0.1, 0.1, 0.9, 0.9] specifies the position and size of the axes in the figure (left, bottom, width, height). The projection='3d' argument specifies that we want to create a 3D plot.

x= np.array(1,5,2,4) # set of values for x and y
y= np.array(1,2,4,5)
plt.subplots(1,2,1)


plt.subplots(1,2,2)

# There is a lot of functions, and formatting in terms of data, numbers, axes etc. it requires some time to understand.