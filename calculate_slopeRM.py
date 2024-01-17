#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 15:56:45 2023

@author: m.kaandorp
"""
import numpy as np
import scipy.stats
import matplotlib.pyplot as plt
import pandas as pd


def time_convert(x):
    h = x.hour
    m = x.minute
    s = x.second
    return (h*60+m)*60+s

def find_max_slope(t,y):

    # Calculate 2 types of slopes: one on 2 points, one on more points if possible
    # 2 points is always possible, so we initialize n_points to 2, and R to 1.
    # We want the highest slope in the dataset, so we set the initial value to -infinity
    slope_max_2p = -np.inf
    slope_max_R95 = -np.inf
    n_points = 2
    R = 1.
    i_start_2p = 0
    i_start_R95 = 0
    i_start = 0
    
    # Here we loop through the datapoints (time)
    for i1 in range(len(t)-1):
        
        # this is a simple slope calculation for two points: dy/dt
        slope_2p = (y[i1+1] - y[i1]) / (t[i1+1] - t[i1])
        if slope_2p > slope_max_2p:
            slope_max_2p = slope_2p
            i_start_2p = i1
            
        # now we loop through the remaining points, to see if there is a slope
        # with more than 2 points with an R>.95
        for i2 in range(i1+n_points_min,len(t)):
        # for i2 in range(i1+5,len(t)):
            
            # we use scipy to fit the data
            fit = scipy.stats.linregress(t[i1:i2],y[i1:i2])
            if fit.rvalue**2 > .95:
                if fit.slope > slope_max_R95:
                    slope_max_R95 = fit.slope
                    n_points = len(t[i1:i2])
                    R = fit.rvalue
                    i_start_R95 = i1
                    
    # We use the slope calculated from multiple points if possible, otherwise the 2-point slope                
    slope_use = None
    if slope_max_R95 > -np.inf:
        slope_use = slope_max_R95
        i_start = i_start_R95
    else:
        slope_use = slope_max_2p
        i_start = i_start_2p
        
    # output everything that is interesting here
    return slope_use, slope_max_2p, slope_max_R95, n_points, R, i_start

# minimum points for calculating slope
n_points_min = 3

#Parameters for Lambert Beersche Formula --> DeltaOD[min-1]*Vol in MTP [ml]*dilution factor/ d[cm]*extinktion koefficient [mM-1*cm-1]☺*vol. of sample [ml] = U/ml --> /used enzyme konzentration [mg/ml} = U/mg
vol_in_mtp = 0.2 #0.08 #0.2 #volume in mtp ml
dil_fac = 1 #dilution factor
d_thick = 0.625 #0.73 #0.625 #d[cm] Schicktdicke
ext_koeff = 10 #Extinktion koefficient [mM-1*cm-1] bei pH 8 zu 15 ändern bei pH 7 10
vol_of_samp = 0.01 #0.0025 #0.01 #ml volume of sample
enz_konz = 0.003125 #0.003125 #mg/ml enzyme used 
output_name = 'results_pNPH_40°C_HoceMut_0,003125_UMG_N3.xlsx'


data = pd.read_excel('../RawData/02052023 pnpH + Impranil alle + mut 0,03125.xlsx',sheet_name='pNPH 40°C ocemut')
t = data['Time(hh:mm:ss)'].apply(time_convert).values/60


slopes_blank = {}
slopes_enzyme = {}
for name in data.keys()[2:]:

    # here: y = -data[name] for negative slopes (Impranil)
    y = data[name]
    
    results = find_max_slope(t,y)
    
    slope = results[0]
    n_points = results[3]
    Rsquared = results[4]**2
    i_start = results[5]
    
    plt.figure()
    plt.plot(t,y,'o-')
    plt.plot([t[i_start],t[i_start]],[0,3],'k:') #yellow numbers define dashed line left
    plt.plot([t[i_start+n_points-1],t[i_start+n_points-1]],[0,3],'k:') #yellow numbers define dashed line right
    plt.title('%s, slope: %3.3f, R2: %3.3f, Enzyme conz: %f' % (name,slope,Rsquared,enz_konz)) #define output in graph, % means give out number, f means float means decimal number
    plt.xlabel('Time [min]')

    if 'Blank' in name:
        slopes_blank[name] = slope
    elif 'Empty' in name:
        pass
    else:
        slopes_enzyme[name] = slope
    
    

slope_blank = np.mean(list(slopes_blank.values()))    
   
results_enzyme = {}
for enz in slopes_enzyme.keys():
    
    slope = slopes_enzyme[enz]
    
    slope = slope - slope_blank 
    
    result = ((slope * vol_in_mtp * dil_fac) / (d_thick * ext_koeff * vol_of_samp)) / enz_konz
    
    results_enzyme[enz] = result
    
    
    
#%% create data with unique enzymes

keys_unique  = []
vals_unique = {}

for key_ in results_enzyme.keys():
    
    key_enz = key_.split('.')[0]
    
    if key_enz in keys_unique:
        vals_unique[key_enz].append(results_enzyme[key_])
    else:
        keys_unique.append(key_enz)
        vals_unique[key_enz] = []
        vals_unique[key_enz].append(results_enzyme[key_])
        
        
pd.DataFrame(data=vals_unique.values(),index=vals_unique.keys()).to_excel('../Results/' + output_name)
    









    
    
    