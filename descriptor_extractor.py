#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 09:28:10 2019

@author: florianpgn
"""

import numpy as np

from csv_read import readData
from importlib import reload
from define_names import define_names

import re
import h5py_file_tool as hft
import params
import data_quartiles
import data_post_processing as post_pro

reload(params)    


def cleanExe(exe):
    """
    Remove the .exe part at the end of the string and replace all other 
    non-alphanumeric characters
    """
    exe = exe[:-4]
    return re.sub('[^A-Za-z0-9]+','', exe)

def sortExes(table):
    """
    Sort by frequency   
    """
    # Return the number of occurences of each exe
    arr, counts = np.unique(table, return_counts=True)
    
    # Minus because we want to order in decreasing order (most occurences to less)
    # Argsort so that it gives us the index of the exe which corresponds to the counter 
    sorted_counts = np.argsort(-counts)
    sorted_table = arr[sorted_counts]
    for (i, string) in enumerate(sorted_table):
        print(i+1,':', string)
        
    return sorted_table

def getTitleCodes(window_title):
    """
    Retrieve window title codes and do some further processing to deal with
    full-width/half-width katakana and character encoding
    """
    title_names = define_names()[1]
    
    # We start at index 2 because Debug and Test need to be dealt with differently
    title_codes = [code.encode('utf-8') for code in title_names[2:] if code in window_title]
    
    if "Debug" in window_title or "デバッグ" in window_title or "ﾃﾞﾊﾞｯｸﾞ" in window_title:
        title_codes.insert(0,title_names[0].encode('utf-8'))
    if "Test" in window_title or "テスト" in window_title or "ﾃｽﾄ" in window_title:
        title_codes.insert(0,title_names[1].encode('utf-8'))
    
    title_codes += [b''] * (3 - len(title_codes))
    return title_codes

    
def timeToLunchCode(time) :
    """
    Get rid of the date, we only deal with the time
    """
    time = time[11:]
    time = np.array(time.split(':'), dtype=int)
    
    return 1 if time[0] == 12 and 30 < time[1] and time[1] < 59 else 0
        

if __name__ == "__main__":
      
    data = readData(params.ANNOTATION_FILE)
    data = post_pro.addDurationFeature(data)
        
    titles = np.array([getTitleCodes(title) for title in data[params.WINDOW_STR]])
    
    exes = np.array([cleanExe(exe).encode('utf-8') for exe in data[params.EXE_STR]])
    
    lunch = np.array([timeToLunchCode(time) for time in data[params.TIME_START_STR]])
    
    print('Keystrokes')
    keystrokes = np.array([int(n) for n in data[params.NB_KSTROKES_STR]])
    keystrokes = data_quartiles.get_quartiles(keystrokes, params.N_BINS_KSTROKES, False)
    
    print('Duration')
    duration = data[params.DURATION_STR]
    duration = data_quartiles.get_quartiles(duration, params.N_BINS_DURATION, False)
    
    print('L clicks')
    l_clicks = np.array([int(n) for n in data[params.NB_LCLICK_STR]])
    l_clicks = data_quartiles.get_quartiles(l_clicks, params.N_BINS_LCLICKS, False)
    
    r_clicks = np.array([int(n) for n in data[params.NB_RCLICK_STR]])
    ## You may also try to binarize right clicks
    #r_clicks[r_clicks>0]= 1
    
    tasks = np.array(data[params.HAND_TASK_STR])
    
    if not params.HIERARCHICAL:
        """
        In stage-1, we label everything that is not TEST or DOCUMENT as OTHER
        """
        if params.STAGE == 1:
            tasks[np.invert(np.logical_or(tasks == params.TEST, \
                                          tasks == params.DOCUMENT))] = params.OTHER
        """
        In stage-2 we select all the samples, where the associated task is PROG, 
        ADMIN or LEISURE
        """
        else:
            boolean_matrix = (tasks == np.array(params.TASKS)[:,None])
            query_array = boolean_matrix.any(axis=0) # Logical or between rows
            tasks = tasks[query_array]
            titles = titles[query_array]
            exes = exes[query_array]
            lunch = lunch[query_array]
            keystrokes = keystrokes[query_array]
            duration = duration[query_array]
            l_clicks = l_clicks[query_array]
            r_clicks = r_clicks[query_array]
      
    tasks = [task.encode('utf-8') for task in tasks]
    
    
    
    """
    Save features in .dat files
    """
    hft.save(params.PATH_TASK[6:]+params.NEW_DAT+params.TASK_MAT, [tasks], [params.TASK_MAT])
    hft.save(params.PATH_EXE[6:]+params.NEW_DAT+params.EXE_MAT, [exes], [params.EXE_MAT])
    hft.save(params.PATH_TITLE[6:]+params.NEW_DAT+params.TITLE_MAT, [titles], [params.TITLE_MAT])
    hft.save(params.PATH_LUNCH[6:]+params.NEW_DAT+params.LUNCH_MAT, [lunch], [params.LUNCH_MAT])
    hft.save(params.PATH_DURATION[6:]+params.NEW_DAT+params.DURATION_MAT, [duration], [params.DURATION_MAT])
    hft.save(params.PATH_KSTROKES[6:]+params.NEW_DAT+params.KSTROKE_MAT, [keystrokes], [params.KSTROKE_MAT])
    hft.save(params.PATH_CLICKS[6:]+params.NEW_DAT+params.LCLICK_MAT, [l_clicks], [params.LCLICK_MAT])
    hft.save(params.PATH_CLICKS[6:]+params.NEW_DAT+params.RCLICK_MAT, [r_clicks], [params.RCLICK_MAT])
    
    with open(params.PATH_TITLE[6:]+params.NEW_DAT+params.TITLE_MAT+'.txt', 'w') as f:
        for item in data[params.WINDOW_STR]:
            f.write("{}\n".format(item))
            
    with open(params.PATH_KSTROKES[6:]+params.NEW_DAT+params.KSTROKE_MAT+'.txt', 'w') as f:
        for item in keystrokes:
            f.write("{}\n".format(item))

        
    """
    This part is to display some statistics about the data, 
    Min, Max, Average and Standard deviation
    """
    """
    t_l_clicks = np.array([int(n) for n in data[params.NB_LCLICK_STR]])
    t_keystrokes = np.array([int(n) for n in data[params.NB_KSTROKES_STR]])
    t_r_clicks = np.array([int(n) for n in data[params.NB_RCLICK_STR]])
    t_duration = data[params.DURATION_STR]
    arr = [t_l_clicks, t_r_clicks, t_keystrokes, t_duration]
    for table in arr:
        print(f'Min : {np.min(table)}, Max : {np.max(table)}, Avg : {np.average(table):.2f}, Std : {np.std(table):.2f}')    
    """ 
