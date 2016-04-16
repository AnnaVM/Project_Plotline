'''
this script gets the emotion counts in the movie scripts contained in the file
'../data/new_scraping/texts/'

the progression of emotion counts can be followed on the terminal

this is based on the lexicon NRC_emotions.txt (placed in '../data/emotions/')
--> for more information on the NRC Word-Emotion Association Lexicon, visit
    'http://saifmohammad.com/WebPages/NRC-Emotion-Lexicon.htm'

8 emotions covered + positive/negative sentiment: anger, anticipation, disgust,
    fear, joy, negative, positive, sadness, surprise, trust

Usage:
------
To execute this script, type in a terminal
$ python emotions_script.py

Challenges --> choices:
-----------------------
increasing speed of code: i) read NRC_emotions.txt into a dataframe,
                          ii) pivot dataframe (to have word as index),
                          iii) export to dictionary (word as key, 0/1s as array)
                          iv) pretty obvious: vocabulary as set
detecting emotions: words are lemmatized (time consumming operation)
                   i) not stemmed, to keep real words to look up
                   ii) sarcastic phrasing, or negative phrases, are not detected
                    ('he was not happy' --> 'happy' will count as positive)

Files created:
--------------
in ../data/emotions/arrays folder: all of the emotion counts available in .npy
'''

import pandas as pd
import numpy as np
import os
from plotline_utilities import progression_bar

from nltk.stem import WordNetLemmatizer

def load_dictionary_and_vocabulary(filename):
    '''
    parameters:
    -----
    filename to the word-emotion association lexicon

    returns:
    --------
    dictionary with word as index and 0/1 value for related emotion in columns
    (anger, anticipation, disgust, fear, joy, negative,
    positive, sadness, surprise, trust)
    set of vocabulary, ie all the words that appear in the dictionary

    '''
    # Load the NRC emotions
    emotion_df = pd.read_csv(filename,
                     delim_whitespace=True, header=None)
    reshaped_df = emotion_df.pivot( 0, 1, 2 )

    # Get the list of existing words
    vocabulary = set( emotion_df[0].unique() )

    # Convert to dictionary
    emotion_dict = {}
    for word in list( vocabulary ):
        emotion_dict[word] = reshaped_df.ix[ word ].values
    return emotion_dict, vocabulary

#######text clean-up (lemmatize, lowercase)
def get_clean_text(list_filenames, path_to_file):
    '''
    parameter:
    ----------
    list_filenames: as LST is a list of filename as STR
    path_to_file: as STR is the path to the file containing movie scripts
    --> such that path_to_file/filename.txt is the file to open

    returns:
    --------
    list of list of words (lemmatize, lowercase) in the text (order preserved)
    '''
    wnl = WordNetLemmatizer()
    list_texts_as_words = []
    for filename in list_filenames:
        path_file = path_to_file+"/"+filename+".txt"
        with open(path_file) as f:
            text = f.readlines()
            lines = [line.strip() for line in text if line.strip()]
            string_words = []
            for line in lines:
                words = [wnl.lemmatize(word.lower()) for word in line.split(' ') if wnl.lemmatize(word.lower())]
                string_words += words
        list_texts_as_words.append(string_words)
    return list_texts_as_words

#######get chunks of text
def window_blocks(text, size_block=100):
    '''
    parameters:
    -----------
    text: list of words in a textfile
    size_block: size of the window (how many consecutive words to
                add to a window)

    returns:
    --------
    the text as a list of windows (window = list of words of length size_block)
    '''
    list_windows = []
    for i in xrange(0,len(text)-size_block,size_block):
        window = text[i:i+size_block]
        list_windows.append(window)
    return list_windows

def emotion_counts(list_words, emotion_dict, vocabulary):
    '''
    parameters:
    -----------
    list of words (typically 100 words long)
    emotion_dict: dictionary
        Contains the information of the NRC database, represented as:
        - A word as a key
        - A 1darray of shape (10,) containing 0s or 1s, as a value
        Each element of the array corresponds to one of the emotions/sentiments

    vocabulary: set
        The unique words for which we have emotions in the NRC database

    returns:
    --------
    emotion_counts: array with the emotion count for the 8 emotions +
                    positive/negative sentiment
    '''
    # Initializing an array of 8 emotions + 2 sentiments (positive/negative).
    # Order:
    # anger, anticipation, disgust, fear, joy, negative,
    # positive, sadness, surprise, trust
    emotion_count = np.zeros(10)

    #counting the number of words in each emotion
    for word in list_words:
        if word in vocabulary:
            #looking up the word
            emotion_for_word = emotion_dict[ word ]
            # Adding up the emotions
            emotion_count += emotion_for_word

    return emotion_count

def get_emotions(filename, path_to_file, emotion_dict, vocabulary,
                 print_to_file=False,
                 verbose=False):
    '''
    parameters:
    -----------
    filename: as STR
    path_to_file: as STR
        such that 'path_to_file/filename.txt' is the script being analyzed
    emotion_dict: dictionary with word as key and 0/1s in array as value (see
        load_dictionary_and_vocabulary function)
    vocabulary: all the words from the previous dictionary in set
    print_to_file: BOOL gives the option to save the counts as array in
                    ../data/emotions/arrays/filename.npy
    verbose: BOOL that prints progress (every 10 windows treated)

    returns:
    --------
    '''
    text = get_clean_text([filename], path_to_file)[0]
    list_windows = window_blocks(text, size_block=100)
    if verbose:
        print 'New file:', len(list_windows)
    list_emotions=[]
    index = 0
    for window in list_windows:
        index +=1
        list_emotions.append(emotion_counts(window, emotion_dict , vocabulary))
        if index%10==0 and verbose:
            print index
    array_emotions = np.array(list_emotions)
    if print_to_file:
        path_to_file = "../data/emotions/arrays/"+filename
        np.save(path_to_file, array_emotions)
    return array_emotions

if __name__ == '__main__':
    NRC_emotions_file = '../data/emotions/NRC_emotions.txt'
    print 'Loading the NRC emotions database, please wait.'
    emotion_dictionary, vocabulary = \
                            load_dictionary_and_vocabulary(NRC_emotions_file)

    # Create the proper directories
    if not os.path.exists('../data/emotions/arrays'):
        os.mkdir('../data/emotions/arrays')

    # Loop through the script files
    path_to_file = '../data/scraping/texts'
    files = os.listdir(path_to_file)
    index = 1
    legit_files = [filename for filename in files if filename[-3:]=='txt']
    Ntot = len(legit_files)
    for filename in legit_files:
        get_emotions( filename[:-4], path_to_file, emotion_dictionary,
                    vocabulary, print_to_file=True, verbose=False)
        progression_bar(index, Ntot, Nbars=60, char='-')
        index += 1
