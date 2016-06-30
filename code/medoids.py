'''
usage:
------
3 actions are possible with this script:

i) to see the costs associated with the number of clusters

$ python medoids.py pick_k

ii) to get a clustering done with, here 3 clusters

$ python medoids.py k=3

iii) to investigate how stable the 3 clusters are when the clustering
is done several times (change 3 to number of clusters chosen)

$ python medoids.py 3_stability

'''

# fonctions: cluster, assign_points_to_clusters, compute_new_medoid
#from : https://github.com/salspaugh/machine_learning/blob/master/clustering/kmedoids.py
# AnnaVM added some of the comments and most of the docstring
#!/usr/bin/env python

import cPickle as pickle
import matplotlib.pyplot as plt
from plotline_utilities import progression_bar
from collections import defaultdict
from seaborn import heatmap
import numpy as np
import pandas as pd
import random
import sys

def cluster(distances, k=3):
    '''
    parameters:
    ----------
    distances: square np.array of size m x m, with m the number of datapoints
    k: number of clusters

    returns:
    --------
    cluster: np.array giving for each datapoint the number of the cluster it
            belongs to.
    curr_medoids: np.array of indices of the datapoints which are the medoids
    '''

    m = distances.shape[0] # number of datapoints

    # Pick k random medoids. initialize the array, then fill it with k different
    #integers (each interger is the index of the datapoint used to initialize
    #the cluster)
    curr_medoids = np.array([-1]*k)
    while not len(np.unique(curr_medoids)) == k:
        curr_medoids = np.array([random.randint(0, m - 1) for _ in range(k)])
    old_medoids = np.array([-1]*k) # Doesn't matter what we initialize these to.
    new_medoids = np.array([-1]*k)

    # Until the medoids stop updating, do the following:
    while not ((old_medoids == curr_medoids).all()):
        # Assign each point to cluster with closest medoid.
        clusters = assign_points_to_clusters(curr_medoids, distances)

        # Update cluster medoids to be lowest cost point.
        for curr_medoid in curr_medoids:
            #consider only the points around the current medoid
            cluster = np.where(clusters == curr_medoid)[0]
            #get the new medoid
            new_medoids[curr_medoids == curr_medoid] = compute_new_medoid(cluster, distances)

        old_medoids[:] = curr_medoids[:]
        curr_medoids[:] = new_medoids[:]

    return clusters, curr_medoids

def assign_points_to_clusters(medoids, distances):
    '''
    returns:
    -------
    clusters: np.array (1d) of size m, with m the number of datapoints
             gives index of cluster for each datapoint
    '''
    #look at the distance to the medoids (referenced by index)
    distances_to_medoids = distances[:,medoids] #size k columns, m rows
    #choose smallest distance
    clusters = medoids[np.argmin(distances_to_medoids, axis=1)] # m colums, 1 row
    clusters[medoids] = medoids #make sure to have a medoid in its own
    return clusters

def compute_new_medoid(cluster, distances):
    mask = np.ones(distances.shape)
    mask[np.ix_(cluster,cluster)] = 0.
    cluster_distances = np.ma.masked_array(data=distances, mask=mask, fill_value=10e9)
    costs = cluster_distances.sum(axis=1)
    return costs.argmin(axis=0, fill_value=10e9)

def cost(curr_medoids, clusters, distances):
    '''
    average distance in clusters (sum(distance(point one to others in cluster)))/num point in cluster
    my own added function
    '''
    list_average_costs = []
    for curr_medoid in curr_medoids:
        #defines the cluster with indices and gets num of elements
        #in the cluster
        cluster_ = np.where(clusters == curr_medoid)[0]
        num_movies = len(cluster_)
        mask = np.ones(distances.shape)
        #add zeros everywhere that belongs to cluster
        mask[np.ix_(cluster_,cluster_)] = 0.
        cluster_distances = np.ma.masked_array(data=distances, mask=mask, fill_value=10e9)
        costs = cluster_distances.sum(axis=1)
        #get average_cost for cluster:
        avg_cost = sum(costs.data)*1./num_movies
        list_average_costs.append(avg_cost)
    return curr_medoids, list_average_costs, np.mean(list_average_costs)

###########################    added on      ###########################
###########################    functions     ###########################
###########################    by AnnaVM     ###########################

def make_distance_array(distance_dictionary):
    '''
    parameters:
    -----------
    Takes in the pickled dictionary (d[movie1][movie2]=distance)

    Returns:
    --------
    list of movies (from the dictionary)
    np.array (square array of size num movies) as the matrix of
    pairwise distances
    '''
    movies = distance_dictionary.keys()
    list_distances = []
    for movie1 in movies:
        movie_distances = []
        for movie2 in movies:
            if movie1 == movie2:
                movie_distances.append(0)
            else:
                movie_distances.append(distance_dictionary[movie1][movie2])
        list_distances.append(movie_distances)
    distances = np.array(list_distances)
    return movies, distances

def clusters_k(k, distances, plot_option=False):
    '''
    k custers are formed with the medoids algorithm
    the procedure is repeated 100 times to ensure with find global, not local minimum

    parameters:
    -----------
    k: number of clusters
    distances: square matrix of pairwise distances
    plot_option: seeing the costs as bar graph

    return:
    -------
    mini: the minimum cost encountered
    medoids: the medoids ('center of clusters') correponding to the minimum cost
    '''
    list_values = []
    mini = 10e9
    index = 0
    for _ in xrange(100):
        #the clustering runs 100 times, we keep the best one (in an attempt to get the )
        clusters, curr_medoids = cluster(distances, k=k)
        curr_medoids, list_average_costs, avg_cost = cost(curr_medoids, clusters, distances)
        if plot_option:
            plt.bar(xrange(len(list_average_costs)), list_average_costs, label=avg_cost)
            plt.legend()
            plt.title(index)
            plt.show()
        index +=1
        list_values.append([curr_medoids, list_average_costs, avg_cost])
        if avg_cost<mini:
            mini = avg_cost
            medoids = curr_medoids
    return mini, medoids

def defining_k(distances, range_k=range(2,15), plot_option=True):
    '''
    parameters:
    -----------
    distances: square matrix of pairwise distances
    range_k: list of the number of clusters to explore
    plot_option: see the cost

    return:
    -------
    list_val: list of costs
    list_medoids: list of medoids
    --> both are in the same order as range_k
    '''
    list_val = [] #will receive the cost of the clustering
    list_medoids = [] #will receive the medoids
    for k in range_k:
        print 'executing for ' + str(k) + ' clusters'
        mini, curr_medoids = clusters_k(k,distances)
        list_val.append(mini)
        list_medoids.append(curr_medoids)
    if plot_option:
        plt.plot(range_k, list_val, '-x')
        plt.xlabel('num of clusters')
        plt.ylabel('cost')
    return list_val, list_medoids

def chosen_num_cluster(movies, chosen_k, distances):
    '''
    parameters:
    -----------
    movies: list of movies
    chosen_k: the number of cluster chosen (needs to be >=2)
    distances: square array of pairwise distances

    returns:
    --------
    a list of the movies that are the medoids as INT eg: [833, 456, 678]
    a list of the movies that are the medoids as STR (filename) eg: [movie833, movie456, movie678]

    a list of the cluster each movie belongs to (cluster833, cluster456, cluster833, ...)

    a dictionary
    a list of cluster as STR (filename)
    '''

    #do the clustering and keep smallest cost for 100 tries
    mini, curr_medoids = clusters_k(chosen_k,distances)

    movies_array = np.array(movies)
    chosen_medoids = curr_medoids

    #list the medoids (as number + name)
    chosen_medoids_array = np.array(chosen_medoids)
    medoid_movies = movies_array[chosen_medoids_array]

    #get the clusters to which each point belongs
    clusters = assign_points_to_clusters(chosen_medoids, distances)

    #seperate out the clusters:
    dict_clusters_mask = {}
    dict_clusters_movie_names = {}
    for medoid in chosen_medoids:
        boolean_array = (clusters == medoid)
        movies_in_cluster = movies_array[boolean_array]
        dict_clusters_movie_names[medoid] = movies_in_cluster
        dict_clusters_mask[medoid] = boolean_array


    return  chosen_medoids, medoid_movies, \
            clusters, \
            dict_clusters_mask, dict_clusters_movie_names

def see_histograms(list_distances):
    plt.figure(figsize=(10,10))
    n_cluster = len(list_distances)
    if n_cluster%2 == 0:
        n_rows = int(n_cluster/2)
    else:
        n_rows = int(n_cluster/2) + 1
    index = 0
    for cluster_distances in list_distances:
        plt.subplot(n_rows, 2, index+1)
        plt.hist(cluster_distances, bins=20)
        plt.xlabel('distance from medoid')
        plt.ylabel('count of movies')
        plt.title('cluster '+ str(index)+ ' (population: '+ str(len(cluster_distances)) + ')')
        index +=1
    plt.tight_layout()
    plt.show()

def see_heatmap(d_intracluster_distances, dict_clusters_mask):
    #create a symetrical pandas dataframe
    df = pd.DataFrame(d_intracluster_distances, columns=dict_clusters_mask.keys())
    #rename column to have right label in heatmap
    d_column = {}
    n_column = 0
    for key in dict_clusters_mask.keys():
        d_column[key] = n_column
        n_column += 1
    df.rename(columns=d_column, inplace=True)

    heatmap(df,annot=True)
    plt.show()

def visualize_clusters(dict_clusters_mask, dict_clusters_movie_names,distances):
    #distances in cluster
    list_distances = []
    d_intracluster_distances = {}
    for cluster1, bool_array in dict_clusters_mask.items():
        list_distances.append(distances[bool_array][:,cluster1])
        list_for_dict = []
        for cluster2, bool_array2 in dict_clusters_mask.items():
            pp = distances[bool_array][:, bool_array2]
            list_for_dict.append(np.median(pp))
        d_intracluster_distances[cluster1] = list_for_dict

    see_histograms(list_distances)
    see_heatmap(d_intracluster_distances, dict_clusters_mask)

    return list_distances, d_intracluster_distances

def investigate_stability(movies, distances, times_run, k):
    '''
    exploring the stability of the clusters
    the clustering (with 100 initiations to enhance the chance of reaching the global minimum)
    is run multiple times

    parameters:
    -----------
    movies: list of movies
    distances: square array of pairewise distances
    k: number of clusters
    times_run: number of times the clustering is run (for instance 6 or 10)

    returns:
    --------
    dictionary with the stable sets
    '''
    list_runs = [] #will get all the movies as filename in the clusters
                   # for instance k = 3:
                   # [[set1, set2, set3], [set1, set2, set3]]
    print 'Progression of clustering'
    for i in xrange(times_run):
        progression_bar(i, times_run-1, Nbars=times_run-1, char='-')
        #for a run let's get the clusters
        m1,m2,c,d1,d2 = chosen_num_cluster(movies, k, distances)
        list_sets = [] # will receive the sets: [set1, set2, set3]
        for key in d2.keys():
            s1 = set(d2[key])
            s1.add(key)
            list_sets.append(s1)
        list_runs.append(list_sets)

    medoids = m2 #the medoids can vary with the runs, but they should be in the same
                 #clusters, this will allow us to id clusters in different clusters

    #figure out corresponding clusters from the various runs, and bringing them together
    d = defaultdict(list)
    #dictionary: d[medoid] = [set1_from_run1, set3_from_run2, ...] containing the medoid
    for run in list_runs:
        for set_ in run:
            for medoid in medoids:
                if medoid in set_: #identify the right cluster
                    d[medoid].append(set_)

    #finally, intersect the sets
    d_intersection = {}
    for medoid in d.keys():
        list_sets = d[medoid]
        for i in range(len(list_sets)):
            if i == 0:
                set_intersect = list_sets[i]
            else:
                set_intersect = set_intersect.intersection(list_sets[i])
        d_intersection[medoid] = set_intersect

    #print the stability: how many movies are always together in the same cluster
    num_movies = 0
    total_num_movies = len(movies)
    print '\n'
    print '*'*50
    print '**' + ' '*12 + 'stability of clusters' + ' '*13 +'**'
    print '*'*50
    for intersect_set in d_intersection.values():
        num_movies += len(intersect_set)
        print 'number of movies always in the cluster: '+ str(len(intersect_set))
    print '-'*50
    print 'movies that are always in the same cluster: '
    print 'in numbers: '+ str(num_movies) + ' | in percent: ' + str(num_movies*1./total_num_movies * 100) +'%'
    print '*'*50

    return d_intersection

if __name__ == '__main__':
    #getting distances in a dictionary
    with open('../data/distances.pkl', 'r') as f:
        distance_dictionary = pickle.load(f)
    #getting distances as a square array
    movies, distances = make_distance_array(distance_dictionary)

    if sys.argv[1] == 'pick_k':
        list_val, list_medoids = defining_k(distances, range_k=range(2,15), plot_option=True)
        plt.show()

    elif sys.argv[1][:-1] == 'k=':
        k = int(sys.argv[1][-1])
        m1,m2,c,d1,d2 = chosen_num_cluster(movies, k, distances)
        list_distances, d_intracluster_distances = visualize_clusters(d1, d2 ,distances)

    elif sys.argv[1][1:] == '_stability':
        k = int(sys.argv[1][0])
        d_stable_clusters = investigate_stability(movies, distances, 10, k)
        with open('../data/clusters.pkl', 'w') as f:
            pickle.dump(d_stable_clusters, f)
