from name import *
import SOAPpy


class SOAPService:
    """A soap service ranking similar authors given author's name as the query.

    Attributes:
        name_instance_dict:
            A dictionary with key: author's name string and value:
            name instance. Note that the author's name is clean after
            instantiation of the Name class.
        id_name_dict:
            A dictionary with key: author_id and value: author's name strings.
            Note that the value is a tuple of clean name and noisy name.
    """
    def __init__(self, name_instance_dict, id_name_dict):
        """Initialize the node with its name.

        Parameters:
            name_instance_dict:
                A dictionary with key: author's name string and value:
                name instance. Note that the author's name is clean after
                instantiation of the Name class.
            id_name_dict:
                A dictionary with key: author_id and value: author's name
                strings. Note that the value is a tuple of clean name and
                noisy name.

        """
        self.name_instance_dict = name_instance_dict
        self.id_name_dict = id_name_dict

    def handle_query_name(self, author_name):
        """Return matched authors given an author's name.

        Parameters:
            author_name:
                A string of author's name. It could be not in the dataset.

        Returns:
            A struct supported by soappy keeping exactly matched author_ids
            and similar author_ids.
        """
        exact_id_name_dict = dict()
        possible_id_name_dict = dict()

        author = Name(author_name)
        author_name = author.name
        if author_name in self.name_instance_dict:
            name_instance = self.name_instance_dict[author_name]
            for id in name_instance.author_ids:
                exact_id_name_dict[id] = self.id_name_dict[id][1]
            for id in name_instance.similar_author_ids:
                possible_id_name_dict[id] = self.id_name_dict[id][1]

        struct = SOAPpy.structType()
        struct._addItem("exact", [])
        for (id, name) in exact_id_name_dict.iteritems():
            struct._addItem("exact", [id, name])
        struct._addItem("similar", [])
        for (id, name) in possible_id_name_dict.iteritems():
            struct._addItem("similar", [id, name])
        return struct

    def handle_query_id(self, author_id):
        """Return matched authors given an author's id.

        Parameters:
            author_id:
                A string of author's id. It could be not in the dataset.

        Returns:
            A struct supported by soappy keeping original name in author.csv
            and alternatives in paperauthor.csv
        """
        author_id = int(author_id)
        author_dict = dict()
        for author_name in self.id_name_dict[author_id][2:]:
            if author_name not in author_dict:
                author_dict[author_name] = 1
            else:
                author_dict[author_name] += 1
        struct = SOAPpy.structType()
        struct._addItem("author", self.id_name_dict[author_id][1])
        struct._addItem("paperauthor", [])
        for (name, number) in author_dict.iteritems():
            struct._addItem("paperauthor", [name, number])
        return struct
