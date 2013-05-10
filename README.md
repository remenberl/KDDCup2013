Before running the algorithm, please ensure the Python 2 version is greater than 2.7.

Package required: 

    Soappy: Mainly used for providing soap service

    sklearn: Mainly used for normalizing vectors. Can be installed following http://scikit-learn.

    org/stable/install.html

    scipy: Mainly used for supporting sparse matrix


name_match.py keeps the main program

	Mode 0 generates the submission file.

	Mode 1 starts the soap service, i.e., your computer becomes the server. (you might not be interested in) 

custome_setting.py keeps all the settings of files and soap address/ports.

soap_client.py is responsible for giving queries to the server which is located in my office by default.

soap_server.py is a class defining the online services the server can provide.

name.py is a class representing a name with its alternatives and authors.

io.py is the file responding to read in csv files, serialization files and generate the submission file.

data/ keeps all csv files
serialize/ keeps all intermediate files (run once)

For the latest performance please check: 

https://docs.google.com/spreadsheet/ccc?key=0Ap0nQ3Fy9DUodDhnRFJORTJFUE9KT051OU5FMWdzY2c&usp=sharing

Now this version touches 0.96539 

