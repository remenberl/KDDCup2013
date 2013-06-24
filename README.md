KDDCup2013 Track 2 by SmallData
=================================

*Before running the algorithm, please ensure the Python 2 version is greater than 2.7.*

Computer configuration suggested:
-------------------------------

    All the code except model 0 has been tested on a PC with 16GB memory with Ubuntu 13.04.
    To run model 0, a 32GB memory machine is needed.

Package required: 
-------------------------------

    [sklearn](http://scikit-learn.org/stable/install.html): Mainly used for normalizing vectors.

    scipy: Mainly used for supporting sparse matrix.

    fuzzy: Mainly used for computing distance based on sound of the strings.

Files:
---------------------------------
    main.py keeps the entrance of the whole program.

    custome_setting.py keeps all the settings of files and parameters.

    name.py is a class representing a name with its alternatives and author ids.

    io.py is the file responding to read in csv files, serialization files and generate the submission and files for analysis.

    recall_related.py keeps functions from step 2 to step 3, aiming at generating possible duplicate author ids to increasing the recall.

    precision_related.py keeps functions for step 4 to step 6, aiming at finding out the real duplicates and refinement.

    chinese.py keeps name units for chinese names.

    taiwan.py keeps name units for taiwanese names.

    korean.py keeps last names for korean names.

    simple_convert.py transforms nonaskii characters in Author.csv and PaperAuthor.csv to askii characters.

Folders:
------------------------------------
    data/ keeps all csv files

    serialize/ keeps all intermediate files (run once)

    result/ keeps all the saved results like submission files.

    model0/ keeps codes for generating confident author duplicates on all the author ids appeared in both Author.csv and PaperAuthor.csv. The generated result is used for building better coauthor, covenue matrices for the main algorithm.

How to run:
-------------------------------------
1. Install the necessary packages mentioned at beginning.

2. Copy data set into the data/ folder.

3. Run simple_convert.py to generate cleaned Author.csv and PaperAuthor.csv files.

4. Optional and Time consuming: Run model0/main.py to generate confident duplicate authors in the whole dataset

5. Run main.py to generate submission file under result/
