#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 10:44:06 2019

@author: zeynep


"""

import numpy as np

import sys
sys.path.insert(0, '../') 

import define_names
import file_tools as hft

from importlib import reload
import params
reload(params)

import dic_tools as dt
from prettytable import PrettyTable

(exe_names, window_names, time_names, level_of_assoc) = define_names.define_names()

exe_code_mat = hft.load(params.PATH_EXE + params.DAT_FILE_PREFIX + params.EXE_MAT)
title_code_mat = hft.load(params.PATH_TITLE + params.DAT_FILE_PREFIX + params.TITLE_MAT)
task_code_mat = hft.load(params.PATH_TASK + params.DAT_FILE_PREFIX + params.TASK_MAT)

n_notask = np.sum(task_code_mat == 0)
n_singletask = np.sum(task_code_mat != 0)

n_total_lines = len(task_code_mat)
r_notask = n_notask / n_total_lines
r_singletask = n_singletask / n_total_lines


"""
Distibution of principal tasks
"""
count_task = dt.init_dic()
percent_task = dt.init_dic()
task_known = task_code_mat[task_code_mat != 0]

for i, task in enumerate(params.TASKS):
    count_task[task] = np.sum(task_known == i + 1)# / sum(task_known_code_mat(:,1) != 0)
    percent_task[task] = count_task[task] / len(task_known)

task_table = PrettyTable()
task_table.field_names = ['Code', 'Name', 'Count', 'Ratio']
print('******************************')
print('Distibution of principal tasks')
for i, task in enumerate(TASKS, 1):
    task_table.add_row([i, task, count_task[task], round(percent_task[task],3)])
print(task_table)

"""
exe with codes with 24 and above occur very seldom
"""
nb_unique_exes = int(np.max(exe_code_mat))
count_exe = np.zeros(nb_unique_exes)
for i in range(nb_unique_exes):
    count_exe[i] = np.sum(exe_code_mat == i + 1) # sum(person1_exe_code_mat(:,1) <= 23)

a = np.sort(count_exe)[::-1]
b = np.argsort(count_exe)[::-1]
prior_exe = np.divide(count_exe, np.sum(count_exe))

print('\n******************************')
print('Distibution of exe (only top-5)')
exe_table = PrettyTable()
exe_table.field_names = ['Code', 'Name', 'Count', 'Ratio']
for i in range(5): #size(exe_names,1)
    exe_table.add_row([b[i] + 1, exe_names[b[i]], count_exe[b[i]], round(prior_exe[b[i]],3)])
print(exe_table)


top5_ratio = np.sum(prior_exe[b[:5]])
print('Top-5 exe consitute {0:.3f} of the entire applications'.format(top5_ratio))

"""
Distribution of title codes

Note that I take all columns (1~4)
Only cols 1 and 2 are nonzero, col 3 and 4 are all zeros (they are there just 
in case)
"""
nb_unique_titles = int(np.max(title_code_mat))
count_title = np.zeros(nb_unique_titles)
for i in range(nb_unique_titles):
    count_title[i] = np.sum(title_code_mat == i + 1)

a = np.sort(count_title)[::-1]
b = np.argsort(count_title)[::-1]
prior_title = np.divide(count_title, np.sum(count_title))

print('\n******************************')
print('Distibution of window title (principal)')
title_table = PrettyTable()
title_table.field_names = ['Code', 'Name', 'Count', 'Ratio']
for i in range(10): #size(title_names,1)
        title_table.add_row([b[i] + 1, window_names[b[i]], count_title[b[i]], round(prior_title[b[i]],3)])
print(title_table)

top10 = np.sum(prior_title[b[:10]])
print('Top-10 window titles consitute {0:.3f} of the entire applications'.format(top10))
