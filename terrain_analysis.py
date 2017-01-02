# -*- coding: utf-8 -*-

'''
Small example showing surface analysis.

Theory is taken from:
http://www.spatialanalysisonline.com/

A html containing all the functions is supplied:
Functions.html

NN, 2017-01-01
'''

# Import modules
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import numpy as np
from math import atan, tan, sin, cos, pi, sqrt

# Define a nice peaks function. Borrowed from: https://se.mathworks.com/help/matlab/ref/peaks.html
def peaks(x,y):
	# Use numpy to support vectorizing...
	return (3*(1-x)**2 * np.exp(-(x**2) - (y+1)**2) - 10*(x/5 - x**3 - y**5)*np.exp(-x**2-y**2) - 1/3*np.exp(-(x+1)**2 - y**2))

# Create a raster from the function based on the parameters
f_xmin=-3
f_xmax=3
f_ymin=-3
f_ymax=3
f_res = 0.1

# Apply scaling so that cell size becomes 1
dx = dy = 1		# Cell size in x and y direction
xmin=0
xmax=int((f_xmax-f_xmin)/f_res)
ymin=0
ymax=int((f_ymax-f_ymin)/f_res)

# Calculate surface using the function coordinates
x = np.linspace(f_xmin, f_xmax, (f_xmax-f_xmin)/f_res)
y = np.linspace(f_ymin, f_ymax, (f_ymax-f_ymin)/f_res)
x, y = np.meshgrid(x, y)
z = peaks(x,y)

# Scale x and y axis to make cell size 1 and origin to 0
x = (x-f_xmin)/f_res
y = (y-f_xmin)/f_res

# Raise z axis to remove negative values
z += z.max()

# Create elevation model with normal Cartesian coordinates
elevation = np.flipud(z)

# Create empty slope, aspect and hillshade rasters
slope = np.zeros_like(elevation)
aspect = np.zeros_like(elevation)
hillshade = np.zeros_like(elevation)

'''
Iterate through every pixel in the raster except a one pixel border.
i - vertical coordinate running from top to bottom
j - horizontal coordinate running from left to right
'''

for i in range(elevation.shape[0])[1:-1]:
	for j in range(elevation.shape[1])[1:-1]:
		
		'''
		Define surrounding pixels as explained here:
		http://www.spatialanalysisonline.com/HTML/raster_models.htm

		NW  N   NE
		W   Z   E
		SW  S   SE
		'''
		Z = elevation[i,j]
		N = elevation[i-1,j]
		NW = elevation[i-1,j-1]
		NE = elevation[i-1,j+1]
		S = elevation[i+1,j]
		SW = elevation[i+1,j-1]
		SE = elevation[i+1,j+1]
		W = elevation[i,j-1]
		E = elevation[i,j+1]

		'''
		Define partial derivatives in x and y direction
		Use one of the methods described here:
		http://www.spatialanalysisonline.com/HTML/raster_models.htm
		Horns method is probably the best
		'''
		# x-direction
		dz_dx = ((NE + 2*E + SE) - (NW + 2*W + SW)) / (8*dx)

		# y-direction
		dz_dy = ((NW + 2*N + NE) - (SW + 2*S + SE)) / (8*dy)

		'''
		Calculate slope and aspect based on the methods described here:
		http://www.spatialanalysisonline.com/HTML/gradient__slope_and_aspect.htm

		Hint:
		atan, sqrt, pi, abs
		'''

		# Slope
		slope_rad = (atan(sqrt((dz_dx**2) + (dz_dy**2))))
		slope[i,j] = slope_rad * (180/pi)

		# Aspect
		aspect_rad = pi - atan(dz_dy/dz_dx) + ((pi/2)*(dz_dx/abs(dz_dx)))
		aspect[i,j] = aspect_rad  * (180/pi)
		
		'''
		Do hillshade as well:
		http://edndoc.esri.com/arcobjects/9.2/net/shared/geoprocessing/spatial_analyst_tools/how_hillshade_works.htm
		'''
		
		# Hillshade
		altitude = 45
		azimuth = 315
		zenith_rad = (90-altitude) * (180/pi)
		azimuth_rad = (360-azimuth+90) * (180/pi)
		hillshade[i,j] = 255 * abs((cos(zenith_rad) * cos(slope_rad)) + (sin(zenith_rad) * sin(slope_rad) * cos(azimuth_rad - aspect_rad)))

# Plot everything using matplotlib (http://matplotlib.org/)
fig = plt.figure('Surface')

# Plot surface
ax = fig.gca(projection='3d')
surf = ax.plot_surface(x, y, z, rstride=1, cstride=1, cmap=cm.gray, linewidth=0.01)
max_range = np.array([x.max()-x.min(), y.max()-y.min(), z.max()-z.min()]).max() / 2.0
mid_x = (x.max()+x.min()) * 0.5
mid_y = (y.max()+y.min()) * 0.5
mid_z = (z.max()+z.min()) * 0.5
ax.set_xlim(mid_x - max_range, mid_x + max_range)
ax.set_ylim(mid_y - max_range, mid_y + max_range)
ax.set_zlim(mid_z - max_range, mid_z + max_range)
plt.xlabel('x')
plt.ylabel('y')
plt.title('Surface model')


fig = plt.figure('Result')

# Plot elevation
ax = fig.add_subplot(2,2,1)
plt.imshow(elevation, interpolation='nearest', cmap=cm.gray, extent=[xmin,xmax,ymin,ymax])
plt.xlabel('x')
plt.ylabel('y')
plt.axis('equal')
plt.title('Elevation model')
plt.colorbar()

# Add contour
CS = plt.contour(x, y, z, range(-1000,1000,5), linewidths=0.5, colors='y')
plt.clabel(CS, inline=1, fontsize=8, fmt='%d')

# Plot hillshade
ax = fig.add_subplot(2,2,2)
plt.imshow(hillshade, interpolation='nearest', cmap=cm.gray, extent=[xmin,xmax,ymin,ymax])
plt.xlabel('x')
plt.ylabel('y')
plt.axis('equal')
plt.title('Hillshade model')
plt.colorbar()

# Plot slope
ax = fig.add_subplot(2,2,3)
plt.imshow(slope, interpolation='nearest', cmap=cm.jet, extent=[xmin,xmax,ymin,ymax])
plt.xlabel('x')
plt.ylabel('y')
plt.axis('equal')
plt.title('Slope model')
plt.colorbar()

# Plot aspect
ax = fig.add_subplot(2,2,4)
plt.imshow(aspect, interpolation='nearest', cmap=cm.jet, extent=[xmin,xmax,ymin,ymax])
plt.xlabel('x')
plt.ylabel('y')
plt.axis('equal')
plt.title('Aspect model')
plt.colorbar()

plt.show()
