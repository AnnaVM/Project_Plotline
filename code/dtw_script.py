'''
this script gets the distances between smoothed movie plots
i) the raw data as .npy is found in '../data/emotions/arrays'
ii) the data are smoothed with Lowess (see plotline_utilities for the function)
iii) a norm is defined and the distance is computed with dynamic time wrapping

the progression of steps ii) and iii) can be followed on the terminal

Usage:
------
To execute this script, type in a terminal
$ python dtw_script.py

Challenges --> choices:
-----------------------
comparing plots: Dynamic Time Wrapping
                the original python package was very slow. Remi Lehe used numba
                to accelerate the algorithm by a factor 100 (essentially
                removing nested for loops)
definig a norm: taking all emotions into account
                + penalizing big peaks that do not match -->abs(x^2 - y^2)
                the norm is hard coded in the acc_dtw function


Files created:
--------------
in ../data folder: the dictionary of distances is pickled as 'distances.pkl'
        structure key: movie title 1
                  value: key --> movie title 2
                         value --> distance
'''

import acc_dtw
import dtw #original package
import os
from collections import defaultdict
import numpy as np
import cPickle as pickle

from load_plotline import LoadPlotLine
from plotline_utilities import progression_bar

def prepare_smooth_array(filename):
    '''
    returns:
    --------
    np array [time, emotions], with smoothed counts
    time1 [emotion1, emotion2, emotion3,...]
    time2 [emotion1, emotion2, emotion3,...]
    ...
    '''
    plotline = LoadPlotLine(filename)
    plotline.load_emotions()
    plotline.make_emotion_dictionary(list_emotions=range(10))
    return plotline.smoothed_array_emotions


def distance(x, y):
    """
    x, y: 2d arrays where the second dimension is the emotions
    """
    return( abs( (x**2 - y**2).sum(axis=-1) ) )

def get_distance(arr1, arr2, norm=distance, acc_option=True):
    '''
    parameters:
    -----------
    arr1, arr2: np.arrays from prepared_smooth_array function
            np array [time, emotions], with smoothed counts
            time1 [emotion1, emotion2, emotion3,...]
            time2 [emotion1, emotion2, emotion3,...]
    norm: the measure of distance used,
          defaults to a distance than puts more weight on bigger peaks of
          different heights.
    acc_option: defaults to True, to use acc_dtw (accelerated version of Dynamic
    Time Wrapping). Setting option to False leads to standard dtw

    returns:
    --------
    minimum distance

    note: possible to expand to get other things than min_dist
    '''
    if acc_option:
        min_dist, cost_matrix, acc_cost_matrix, wrap_path =\
                            acc_dtw.dtw(arr1, arr2)
    else:
        min_dist, cost_matrix, acc_cost_matrix, wrap_path =\
                        dtw.dtw(arr1, arr2, dist=norm)

    return min_dist

def dtw_dictionary():
    '''
    takes in the .npy files in arrays
    uses de load_plotline to produce a smooth plot (x,y values)
    computes the distance thanks to Dynamic Time Wrapping

    return:
    -------

    '''
    # Loop through the script files
    path_to_file = '../data/emotions/arrays'
    files = os.listdir(path_to_file)
    legit_files = [filename[:-4] for filename in files if filename[-3:]=='npy']
    Ntot = len(legit_files)
    #prepare all arrays
    print "Preparing all the files"
    list_smooth_arrays = []
    index = 0
    for filename in legit_files:
        arr = prepare_smooth_array(filename)
        list_smooth_arrays.append(arr)
        index += 1
        progression_bar(index, Ntot, Nbars=60, char='-')


    #looking at the similarity in the plots
    print "\n"
    print "Computing all the distances"
    full_dictionary = defaultdict(dict)
    index = 0
    for index1 in xrange(len(legit_files)):
        filename1 = legit_files[index1]
        arr1 = list_smooth_arrays[index1]
        for index2 in xrange(index1+1,len(legit_files)):
            filename2 = legit_files[index2]
            arr2 = list_smooth_arrays[index2]
            min_distance = get_distance(arr1, arr2)
            full_dictionary[filename1][filename2] = min_distance
            full_dictionary[filename2][filename1] = min_distance
        index += 1
        progression_bar(index, Ntot, Nbars=60, char='-')
    return full_dictionary

if __name__ == "__main__":
    d = dtw_dictionary()
    with open('../data/distances.pkl', 'w') as f:
        pickle.dump(d, f)
    print "\n"
