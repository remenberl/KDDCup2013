Before running the algorithm, please ensure the Python 2 version is greater than 2.7.

Computer configuration suggested:

    All the code has been tested on a PC with 16GB memory with Ubuntu 13.04.

Package required: 

    sklearn: Mainly used for normalizing vectors. Can be installed following http://scikit-learn.org/stable/install.html

    scipy: Mainly used for supporting sparse matrix

Files:
    main.py keeps the entrance of the whole program.

    custome_setting.py keeps all the settings of files and parameters.

    name.py is a class representing a name with its alternatives and author ids.

    io.py is the file responding to read in csv files, serialization files and generate the submission and analysis file.

    recall_related.py keeps functions from step 2 to step 3, aiming at generating possible duplicate author ids to increasing the recall.

    precision_related.py keeps functions for step 4, aiming at finding out the real duplicates.

    chinese.py keeps name units for chinese names.

    taiwan.py keeps name units for taiwanese names.

Folders:
    data/ keeps all csv files

    serialize/ keeps all intermediate files (run once)
    
    result/ keeps all the saved results like submission files.

For the latest performance please check: 
https://docs.google.com/spreadsheet/ccc?key=0Ap0nQ3Fy9DUodDhnRFJORTJFUE9KT051OU5FMWdzY2c&usp=sharing

Now this version touches 0.978 

