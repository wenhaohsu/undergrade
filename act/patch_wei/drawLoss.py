# -*- coding: utf-8 -*-
"""
Created on Wed May 15 21:10:11 2019

@author: kylab
"""

import matplotlib.pyplot as plt


fig_width=5.75
fig_height=2.5
fig_dpi=300
font_size=8
marker_size=3
line_width=0.5
board_color='#222222'
board_width=1
tick_color='#222222'
line_color='#444444'

fig = plt.figure(figsize=(fig_width,fig_height))
plt.plot(losses,linewidth=line_width,color=line_color)
plt.tick_params(axis='both',labelsize=font_size,colors=tick_color,which='both')
plt.tick_params(axis='x',which='both',direction='in')
plt.tick_params(axis='y',which='both',direction='in')
ax = plt.gca()
#ax.xaxis.grid(which='both') # vertical lines
plt.ylim((0.1,0.7))
ax.set_yticks([0.1,0.3,0.5,0.7], minor=False)
ax.spines['top'].set_linewidth(board_width)
ax.spines['top'].set_color(board_color)
ax.spines['bottom'].set_linewidth(board_width)
ax.spines['bottom'].set_color(board_color)
ax.spines['left'].set_linewidth(board_width)
ax.spines['left'].set_color(board_color)
ax.spines['right'].set_linewidth(board_width)
ax.spines['right'].set_color(board_color)


plt.savefig('3.png',bbox_inches='tight',dpi =fig_dpi)
plt.close('all')
