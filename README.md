Before running the algorithm, please ensure the Python 2 version is greater than 2.7.
Package: Soappy is needed and can be installed with easy_install.

name_match.py keeps the main program.
	Mode 0 generates the submission file.
	Mode 1 starts the soap service, i.e., your computer becomes the server. (you might not be interested in.) 

custome_setting.py keeps all the settings of files and soap address/ports.

soap_client.py is responsible for giving queries to the server which is located in my office by default.

soap_server.py is a class defining the online services the server can provide.

name.py is a class representing a name with its alternatives and authors.
