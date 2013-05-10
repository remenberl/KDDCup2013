#-*- coding: UTF-8 -*-

author_file = "./data/Author.csv"
paper_author_file = "./data/PaperAuthor.csv"
duplicate_authors_file = "./result/duplicate_authors.csv"

#Address for SOAP service
# server_soap_address = "192.168.11.102"
# client_soap_address = "jialu.cs.illinois.edu"

server_soap_address = "127.0.0.1"
client_soap_address = "127.0.0.1"


#Ports for SOAP service
server_port = 5900
client_port = 5900

sequence_matcher_threshold = 0.8
merge_threshold = 0.001

serialization_dir = "./serialize/"
coauthor_matrix_file = "coauthor.seal"
covenue_matrix_file = "covenue.seal"
author_venue_matrix_file = "author_paper.seal"
author_paper_matrix_file = "author_paper.seal"
name_instance_file = "name_instance.seal"
id_name_file = "id_name.seal"
name_statistics_file = "name_statistics.seal"
