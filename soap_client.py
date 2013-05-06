#-*- coding: UTF-8 -*-
from SOAPpy import SOAPProxy
from custom_setting import *

server = SOAPProxy(client_soap_address + ':' + str(client_port))

while True:
    author = raw_input("Type in the name or id of an author:\n")
    if author.isdigit():
        struct = server.handle_query_id(author)
        #Transform the structype provided by soappy to dict.
        struct_as_a_dict = dict((key, getattr(struct, key))
                                for key in struct._keys())
        exact_name = struct_as_a_dict['author']
        possible_name_list = struct_as_a_dict['paperauthor']
        print "Exact Name:"
        print exact_name
        print
        print "Alternatives in paperauthor.csv:"
        for (author_name, number) in possible_name_list:
            print " || " + author_name + " " + str(number),
        print '\n'
    else:
        struct = server.handle_query_name(author)
        #Transform the structype provided by soappy to dict.
        struct_as_a_dict = dict((key, getattr(struct, key))
                                for key in struct._keys())
        exact_id_name_list = struct_as_a_dict['exact']
        possible_id_name_list = struct_as_a_dict['similar']
        print "Exact Match:"
        for (author_id, author_name) in exact_id_name_list:
            print " || " + author_name + ": " + str(author_id),
        print
        print "Similar:"
        for (author_id, author_name) in possible_id_name_list:
            print " || " + author_name + " " + str(author_id),
        print '\n'
