import os
import glob
import shutil
import subprocess

# This is a new script for doing multiple runs of A12GMIN
# which reduces the need for keeping multiple reference data files


def append_key(keyword):
    """This function simply appends an additional keyword to a list"""

    # Store some of the general keywords in a list
    gen_keywords = ['DUMPSTRUCTURES', 'DEBUG', 'RANDOMSEED', 'TRACKDATA', 'AMBER12', 'CENTRE']

    if keyword == "FIXTEMP" or keyword == "FIXSTEP" or keyword == "FIXBOTH" or keyword == "CISTRANS":
        gen_keywords.append(keyword)
        return gen_keywords
    else:
        return gen_keywords


def vary_key(keyword, values, alistofkeywords):
    """This function assigns a new value to a keyword in the other_gen_keywords dict"""

    # Store other keywords that take 'one' parameter in a dictionary
    other_gen_keywords = {'UPDATES': 3000,
                          'DUMPINT': 200,
                          'SAVE': 5,
                          'RADIUS': 3000,
                          'TEMPERATURE': 2.0,
                          'STEP': 3.0,
                          'TIGHTCONV': '1.0D-6',
                          'SLOPPYCONV': '1.0D-2'}

    for val in values:
        # Assign val to the keyword in other_gen_keywords
        other_gen_keywords[keyword] = val
        # Call the function gen_data to create a data file
        gen_data(keyword, val, other_gen_keywords, alistofkeywords)


def gen_data(keyword, val, otherkeys, genkeys):
    """This function creates the data files for A12GMIN"""
    # Create a unique file based on keyword and val
    f = open('data-{0}-{1}'.format(keyword, val), 'a')

    for k, v in otherkeys.items():
        f.write('{0} '.format(k))
        f.write(str(v))
        f.write('\n')

    for key in genkeys:
        f.write('{0}\n'.format(key))

    # Keep these keywords as strings for now
    f.write('MAXIT 2000 6000\n')
    f.write('STEPS 100 1.0\n')


def run_a12gmin():
    """This function runs A12GMIN on the data files that were created"""
    for data_file in glob.glob('data-*'):
        # Copy data_file to data for A12GMIN run
        shutil.copyfile(data_file, 'data')
        # Run A12GMIN
        subprocess.call("A12GMIN")
        # Run gnuplot - make sure gmin.gplt is in cwd 
        args = ['gnuplot', 'gmin.gplt']
        subprocess.call(args)
        # Rename the gmin.png file to a unique name
        new_png_name = '{0}-gmin.png'.format(data_file)
        os.rename("gmin.png", new_png_name)
        # Make a unique directory to contain all the files for the run
        dir_path = './{0}-RUN'.format(data_file)
        os.mkdir(dir_path)
        # Move the gnuplot png file, data_file and A12GMIN output files to dir_path
        shutil.move(new_png_name, dir_path)

        shutil.move('./{0}'.format(data_file), dir_path)
        # And delete data
        os.remove('./data')

        shutil.move('./best', dir_path)
        shutil.move('./markov', dir_path)
        shutil.move('./energy', dir_path)
        shutil.move('./output', dir_path)
        shutil.move('./lowest', dir_path)

        for coords_file in glob.glob('coords*pdb'):
            shutil.move('./{0}'.format(coords_file), dir_path)

        for coords_file in glob.glob('coords*rst'):
            shutil.move('./{0}'.format(coords_file), dir_path)

        # Delete other files from A12GMIN run
        os.remove('./min.out')
        os.remove('./min.rst')

        if os.path.exists('./initial_cis_trans_states'):
            os.remove('./initial_cis_trans_states')

        if os.path.exists('./cis_trans_states'):
            os.remove('./cis_trans_states')


# A list of parameters associated with the keyword which we want to vary
parameters = [2.0, 4.0, 6.0]

if __name__ == '__main__':
    # Pass an additional keyword to the append_key function
    keywords = append_key('FIXBOTH')

    # Pass a keyword you want to vary
    vary_key('STEP', parameters, keywords)

    # Run A12GMIN for the data set 
    run_a12gmin()
