'''
this code contains two classes,
- LoadPlotLine, designed to help the visualisation of .npy files created
 by the emotion_script.
- ExploreData, designed to explore interactively the plots thanks to widgets
(user selects the movie, then the emotions to plot)

the aim is to allow the user to interactively explore the evolution of emotions
in the chosen movie. Open the 'Visualize_Emotions' Jupyter Notebook.
'''

import os
import numpy as np
import matplotlib.pyplot as plt

import ipywidgets as widgets #new version of IPython.htlm
from IPython.display import display
from ipywidgets import fixed

from plotline_utilities import progression_bar, smoothing,\
                               make_title_dictionary, display_widget

class LoadPlotLine(object):
    '''
    From Plutchik: eight primary emotions in alphabetical order
        anger, anticipation, disgust, fear, joy, sadness, surprise and trust.
        2 overall sentiment analysis (positive or negative sentiments) are
        included
    '''
    def __init__(self, filename):
        self.filename = filename
        self.path = "../data/emotions/arrays/"

        self.emotions = ['anger', 'anticipation', 'disgust', 'fear', 'joy',
                            'negative', 'positive', 'sadness', 'surprise',
                             'trust']
        self.colors = ['#ff0000', '#ffa500', '#ff69b4', '#228b22', '#ffff00',
                            'black', 'grey', '#4169e1', '#00bfff', '#7cfc00']
        #color choice is also inspired by Plutchik's wheel of emotions

    def load_emotions(self):
        #retrieves the .npy array
        path_file = self.path + self.filename + '.npy'
        self.array_emotions = np.load(path_file)

    def visualisation_for_emotions(self, list_emotions=range(5)+range(7,10),
                                   raw_data=True,
                                   title_option=True,
                                   save_png=False):
        '''
        plots the evolution of emotion scores for a movie script, with a
        smoothing step

        parameters:
        -----------
        list_emotions: a list of numbers allowing to chose the emotions to plots
                        0 'anger'               5 'negative'
                        1 'anticipation'        6 'positive'
                        2 'disgust'             7 'sadness'
                        3 'fear'                8 'surprise'
                        4 'joy'                 9 'trust'
                      by default, 'positive' and 'negative' are not plotted
        save_png: BOOL, allows to save matplotlib figure as png in
                 "../data/emotions/graphs/"
        '''
        plt.clf()
        plt.subplots_adjust(right=0.73)
        for index in list_emotions:
            emotion_scores = self.array_emotions[:,index]
            emotion = self.emotions[index]
            x,y = smoothing(emotion_scores, frac=0.1)
            if not raw_data:
                x_max = np.max(x)
                x = x*100.0/x_max
                plt.xlabel('Advancement of the script (%)')
            plt.ylabel('Emotion intensity (a.u.)')
            plt.plot(x,y, label=emotion, color=self.colors[index])
            plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
            if title_option:
                plt.title(self.filename)
            if save_png:
                path_save = "../data/emotions/graphs/"+self.filename

                plt.savefig(path_save, transparent=True, format='png')

class ExploreData(object):
    '''
    exploration = ExploreData()
    exploration.explore()
    then select the movie to look at
    '''
    def __init__(self):
        self.filename_to_title, self.title_to_filename = make_title_dictionary()

    def explore(self):
        '''
        this function allows the creation of the widgets and plot
        '''
        select_widget, checkbox_list = self.widget_creation(
                                       filename_to_title=self.filename_to_title,
                                       directory='../data/emotions/arrays'
                                       )
        self.display_widget(self.f_interactive, self.title_to_filename,
                        select_widget, checkbox_list)

    @staticmethod
    def widget_creation(filename_to_title, directory='../data/emotions/arrays'):
        '''
        this function creates the widgets needed to explore the data
        parameters:
        ----------
        filename_to_title: a dictionary with the filename (without extension) as key
                           and the movie title as value
        directory: path, as STR, to the directory containing the npy files to use
                   usually '../data/emotions/arrays'
        returns:
        --------
        a select widget, with the movie titles corresponding to the npy files
                in the selected directory
        several checkbox widgets to choose which emotion to explore
        '''
        #widget for the selection of files:
        path_to_file = directory
        files = os.listdir(path_to_file)
        legit_files = [filename[:-4] for filename in files if filename[-3:]=='npy']
        legit_titles = [filename_to_title[filename] for filename in legit_files]

        select_widget = widgets.Select()
        select_widget.options = legit_titles

        #widgets for the selection of emotions
        list_emotions = ['anger', 'anticipation', 'disgust', 'fear', 'joy',
              'negative', 'positive',
              'sadness', 'surprise', 'trust']
        checkbox_list = [widgets.ToggleButton(value=False, description=emotion) \
                        for emotion in list_emotions]

        return select_widget, checkbox_list

    @staticmethod
    def f_interactive(movie_title,
                      title_to_filename,
                      anger, anticipation, disgust, fear, joy,
                      negative, positive,
                      sadness, surprise, trust):

        '''
        this function allows the creation of the interactive interface
        the output is a graph of the evolution of selected emotions as the
        script unfolds

        parameters:
        -----------
        movie_title: STR, the filename,
                    where filename.npy is the corresponding file
        title_to_filename: a dictionary with the movie title as key
                           and the filename (without extension) as value
        anger, ..., trust: booleans to decide if the emotion will be displayed
        '''
        #taking in the user choice of emotions
        #(list of booleans, in the same order as in the LoadPlotLine class)
        list_emotions = [anger, anticipation, disgust, fear, joy,
                         negative, positive,
                         sadness, surprise, trust]

        #selection of the relevant emotions
        list_integers = []
        for i in xrange(len(list_emotions)):
            if list_emotions[i]:
                list_integers.append(i)

        plotline = LoadPlotLine(title_to_filename[movie_title])
        plotline.load_emotions()
        plotline.visualisation_for_emotions(list_emotions=list_integers,
                                            raw_data=False,
                                            title_option=False,
                                            save_png=False)
        plt.title(movie_title)
        plt.show()

    @staticmethod
    def display_widget(f, title_to_filename, select_widget, checkbox_list):
        '''
        this function creates the interactive window for the user to explore the data
        '''
        i = widgets.interactive(f,
                     movie_title = select_widget,
                     title_to_filename = fixed(title_to_filename),
                     anger=checkbox_list[0],
                     anticipation=checkbox_list[1],
                     disgust=checkbox_list[2],
                     fear=checkbox_list[3],
                     joy=checkbox_list[4],
                     negative=checkbox_list[5],
                     positive=checkbox_list[6],
                     sadness=checkbox_list[7],
                     surprise=checkbox_list[8],
                     trust=checkbox_list[9])

        hbox1 = widgets.HBox([i.children[0]]) #select movie to explore
        hbox2 = widgets.HBox(i.children[6:8]) #positive and negative sentiment analysis
        hbox3 = widgets.HBox(i.children[1:6]+i.children[8:]) #emotions

        display( hbox1 )
        display( hbox2 )
        display( hbox3 )


################
if __name__ == '__main__':
    # Saving pngs
    user_input = raw_input("Do you want to save plots as png (y/n) > ")
    save_png = (user_input == 'y')

    # Create the directory for pngs
    if not os.path.exists('../data/emotions/graphs') and save_png:
        os.mkdir('../data/emotions/graphs')

    # Loop through the script files
    path_to_file = '../data/emotions/arrays'
    files = os.listdir(path_to_file)
    index = 1
    legit_files = [filename[:-4] for filename in files if filename[-3:]=='npy']
    Ntot = len(legit_files)
    chosen_emotions = range(5)+range(7,10)
    #all emotions except positive and negative
    for filename in legit_files:
        plotline = LoadPlotLine(filename)
        plotline.load_emotions()
        plotline.visualisation_for_emotions(list_emotions=chosen_emotions,
                                            save_png=save_png)
        progression_bar(index, Ntot, Nbars=60, char='-')
        index += 1
