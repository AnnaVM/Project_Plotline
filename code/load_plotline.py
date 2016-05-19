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
                               make_title_dictionary

class LoadPlotLine(object):
    '''
    once the class is created, run the load_emotions() function

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
        self.emotion_dictionary_raw = {}
        self.emotion_dictionary_smooth ={}
        #color choice is also inspired by Plutchik's wheel of emotions

    def load_emotions(self):
        #retrieves the .npy array
        path_file = self.path + self.filename + '.npy'
        self.array_emotions = np.load(path_file)

    def make_emotion_dictionary(self, list_emotions=range(5)+range(7,10)):
        '''
        must be run after: load_emotions
        parameters:
        -----------
        list_emotions: a list of numbers allowing to chose the emotions to plots
                        0 'anger'               5 'negative'
                        1 'anticipation'        6 'positive'
                        2 'disgust'             7 'sadness'
                        3 'fear'                8 'surprise'
                        4 'joy'                 9 'trust'
                      by default, 'positive' and 'negative' are not plotted
        '''
        for index in list_emotions:
            emotion_scores = self.array_emotions[:,index]
            emotion = self.emotions[index]
            self.emotion_dictionary_raw[(emotion,index)] = emotion_scores
            x,y = smoothing(emotion_scores, frac=0.1)
            self.emotion_dictionary_smooth[(emotion,index)] = (x,y)

    def global_overview(self, list_emotions=range(5)+range(7,10),
                        percent_min=0, percent_max=1,
                        bar_color='blue',
                        show_option=True):
        '''
        make a bar graph to order the emotions in the script

        parameters:
        -----------
        list_emotions: a list of the numbers representing the emotions that are
                       to be analyzed
        percent_min: INT from 0 to 1, place to start the analysis
                    (0 is beginning of script, 1 is the end)
                    defaults to 0
        percent_max: INT from 0 to 1, place to stop the analysis
                     defaults to 1
        bar_color: the color of the bars on the graph
        show_option: BOOL, on True, will plot the bar graph
                    defaults to True
        )
        '''
        list_total = [] #list that will have tuples to make the graph
        #eg: [(emotion1, total_words), (emotion2, total_words)]
        total_all_emotions = 0.0
        #some of all emotions, to get %

        self.make_emotion_dictionary(list_emotions)
        #makes self.emotion_dictionary_raw
        #makes self.emotion_dictionary_smooth

        for (emotion,index), (x,y) in self.emotion_dictionary_smooth.iteritems():
            x_min = int(percent_min * len(y))
            x_max = int(percent_max * len(y))
            new_y = y[x_min:x_max]
            list_total.append((emotion, sum(new_y)))
            total_all_emotions += sum(new_y)

        #sort the list to find strongest emotions
        list_total.sort(key=lambda (x,y):y)
        ordered_emotions = [tup[0] for tup in list_total]
        percentages = [int(tup[1]/total_all_emotions*100) for tup in list_total]
        positions = np.array(range(len(ordered_emotions)))
        plt.barh(positions, percentages,
                 color=bar_color, height=0.6, alpha=0.5)
        plt.yticks(positions+0.3, ordered_emotions)
        plt.title('Analysis for %d %% to %d %% of the script'\
                    %(percent_min*100, percent_max*100))
        if show_option:
            plt.show()


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
        self.make_emotion_dictionary(list_emotions)
        valid_indices = set(list_emotions)
        for (emotion,index), (x,y) in self.emotion_dictionary_smooth.iteritems():
            if index in valid_indices:
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
        return select_widget, checkbox_list

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
                      sadness, surprise, trust,
                      visulalize_emotions=True,
                      hierarchy_emotions=False,
                      hierarchy_emotions_subplot=False):

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
        visulalize_emotions: BOOL, option to display the plotline
        hierarchy_emotions: BOOL, option the display the bar graph of
                            emotion importance
        hierarchy_emotions_subplot: BOOL, option the display the bar graph of
                            emotion importance for the beginning (20 %), the
                            middle (next 60 %) and the end (last 20 %) of the
                            script
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
        if visulalize_emotions:
            plotline.visualisation_for_emotions(list_emotions=list_integers,
                                                raw_data=False,
                                                title_option=False,
                                                save_png=False)
            plt.title(movie_title)
            plt.show()

        if hierarchy_emotions:
            plotline.global_overview()

        if hierarchy_emotions_subplot:
            plt.figure(figsize=(5,10))
            plt.subplot(3,1,1)
            plotline.global_overview(percent_min=0,
                                     percent_max=.2,
                                     bar_color='green',
                                     show_option=False)
            plt.subplot(3,1,2)
            plotline.global_overview(percent_min=.2,
                                     percent_max=.8,
                                     bar_color='green',
                                     show_option=False)
            plt.subplot(3,1,3)
            plotline.global_overview(percent_min=.8,
                                     percent_max=1,
                                     bar_color='green',
                                     show_option=False)
            plt.tight_layout()
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
                     trust=checkbox_list[9],
                     visulalize_emotions=fixed(True),
                     hierarchy_emotions=widgets.ToggleButton(value=False,
                                        description='See emotion importance for\
                                         the whole script'),
                    hierarchy_emotions_subplot=widgets.ToggleButton(value=False,
                                       description='See emotion importance for\
                                the beginning, middle and end of the script'))

        hbox1 = widgets.HBox([i.children[0]]) #select movie to explore
        hbox2 = widgets.HBox(i.children[6:8]) #positive and negative sentiment analysis
        hbox3 = widgets.HBox(i.children[1:6]+i.children[8:11]) #emotions
        hbox4 = widgets.HBox(i.children[11:12])
        hbox5 = widgets.HBox(i.children[12:])

        display( hbox1 )
        display( hbox2 )
        display( hbox3 )
        display( hbox4 )
        display( hbox5 )


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
