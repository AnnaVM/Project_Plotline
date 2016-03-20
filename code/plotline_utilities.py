import sys

def progression_bar(i, Ntot, Nbars=60, char='-'):
    '''
    Shows a progression bar with Nbars
    parameters:
    -----------
    i: index of the files
    Ntot: total number of files
    Nbars: how many bars to fill
    char: character to show as progression
    '''
    nbars = int( (i+1)*1./Ntot * Nbars )
    sys.stdout.write('\r[' + nbars*char)
    sys.stdout.write((Nbars-nbars)*' '+']')
    sys.stdout.write('%d/%d'%(i, Ntot))
    sys.stdout.flush()
