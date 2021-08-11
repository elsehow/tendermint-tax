#!/usr/bin/env python
# coding: utf-8

# In[ ]:




# In[61]:


DPI   = 300
WIDTH = 1920
HEIGHT= 1080


# In[68]:


import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

def colorFader(c1,c2,mix=0): #fade (linear interpolate) from color c1 (at mix=0) to c2 (mix=1)
    c1=np.array(mpl.colors.to_rgb(c1))
    c2=np.array(mpl.colors.to_rgb(c2))
    return mpl.colors.to_hex((1-mix)*c1 + mix*c2)


def draw_gradient (color1, color2, n_lines=500):
    def remove_whitespace_in_saved_image(plt):
        # mysterious method from https://stackoverflow.com/questions/11837979/removing-white-space-around-a-saved-image-in-matplotlib
        plt.gca().set_axis_off()
        plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, 
                hspace = 0, wspace = 0)
        plt.margins(0,0)
        plt.gca().xaxis.set_major_locator(plt.NullLocator())
        plt.gca().yaxis.set_major_locator(plt.NullLocator())
    fig, ax = plt.subplots(figsize=(WIDTH/DPI, HEIGHT/DPI), dpi=DPI)
    for x in range(n_lines+1):
        ax.axhline(x, color=colorFader(color2, color1, x/n_lines), linewidth=4)
    plt.axis('off')
    remove_whitespace_in_saved_image(plt)
    return plt
    

# c1='#1f77b4' #blue
# c2='yellow' #green
# plt = draw_gradient(c1, c2)
# plt.show()


# In[63]:


# read colors from wal cache
from pathlib import Path
colors_path = Path.home().joinpath('.cache').joinpath('wal').joinpath('colors')
with open (colors_path, 'r') as f:
    colors = f.read().split('\n')

# plt = draw_gradient(colors[3], colors[3])
# plt.show()


# In[67]:


# pick two random colors
from random import choices

c1, c2 = choices(colors, k=2)

plt = draw_gradient(c1, c2)
plt.savefig('gradient.png')


# In[ ]:





# In[ ]:




