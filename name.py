#-*- coding: UTF-8 -*-
import itertools


class Name:
    """Represent a name with its alternatives and authors.

    Attributes:
        name: a string describing the name.
            e.g., "Michael Jordan".
        first_name: a string describing the first name.
        middle_name: a string describing the middle name.
        last_name: a string describing the last name.
        alternatives: a set of all possible names.
        author_ids: a set of all author ids with the exact same name.
        similar_author_ids: a set of all author ids with similar names
    """
    def __init__(self, name):
        """Initialize the instance with a name.

        Parameters:
            name: The name read from the csv file, could be noisy.
        """
        # In case of M.I. Jordan
        name = name.replace('.', ' ').lower()
        self.name = name
        self.__split_name()
        # Make the name less noisy
        self.name = ' '.join(
                    [self.first_name, self.middle_name, self.last_name])
        self.author_ids = set()
        self.similar_author_ids = set()
        self.alternatives = set()

    def __split_name(self):
        """Split a name into first, middle and last names."""
        elements = self.name.split(' ')
        self.first_name = elements[0].strip()
        self.middle_name = ' '.join(elements[1:-1]).strip()
        self.last_name = elements[-1].strip()

    def __shorten_string(self, string):
        """Find initial of a string.

        Parameters:
            string: Input string to find initial.

        Returns:
            The initial character.
        """
        if not string:
            return ''
        else:
            return string[0]

    def __genearte_possible_names(self, (first_name, middle_name, last_name)):
        """Generate all possible names give the full name.

        Parameters:
            (first_name, middle_name, last_name): A tuple composed of
                first, middle and last names.
        Returns:
            A set of all possible names.
        """
        candidates = set()
        #e.g., Michael Jr. Jordan
        candidates.add(' '.join([first_name, middle_name, last_name]))
        #e.g., Michael Jordan
        candidates.add(' '.join([first_name, '', last_name]))
        #e.g., M. Jordan
        candidates.add(' '.join([self.__shorten_string(first_name),
                                 '',
                                 last_name]))
        #e.g., M. J.
        candidates.add(' '.join(
                       [self.__shorten_string(first_name),
                       '',
                       self.__shorten_string(last_name)]
                       ))
        # e.g., Michael J. Jordan
        candidates.add(' '.join(
                       [first_name,
                       self.__shorten_string(middle_name),
                       last_name]
                       ))
        #e.g., M. J. Jordan
        candidates.add(' '.join(
                       [self.__shorten_string(first_name),
                       self.__shorten_string(middle_name),
                       last_name]
                       ))
        #e.g., M. J. J.
        candidates.add(' '.join(
                       [self.__shorten_string(first_name),
                       self.__shorten_string(middle_name),
                       self.__shorten_string(last_name)]
                       ))

        #####################################################
        # Further improvements: alternatives like Mike
        return candidates

    def __generate_all_possible_names(self):
        """Generate all possible names considering all possible permutations.

        Note: compared to generate_possbile_names, this function additionally
            covers the permutations of first, middle and last names.

        Returns:
            A set of all possible names.
        """
        self.alternatives.add(self.name)
        pool = [self.first_name, self.middle_name, self.last_name]
        self.alternatives = self.alternatives.union(self.__genearte_possible_names(pool))
        for permutation in itertools.permutations(pool):
            self.alternatives = self.alternatives.union(
                self.__genearte_possible_names(permutation))
        self.alternatives = self.alternatives.difference(set([self.name]))
        return self.alternatives

    def get_alternatives(self):
        """Get all possible names.

        Note: This function will call generate_all_possible_names automatically
            if self.alternatives is empty.

        Returns:
            A set of all possible names.
        """
        self.__generate_all_possible_names()
        return self.alternatives

    def add_alternative(self, alternative):
        self.alternatives.add(alternative)

    def add_author_id(self, author_id):
        """Add author_id which matches the name into set author_ids.

        Parameters:
            author_id: Id of the author.
        """
        self.author_ids.add(author_id)

    def add_similar_author_id(self, author_id):
        """Add author_id which has similar name into set similar_author_ids.

        Parameters:
            author_id: Id of the author.
        """
        self.similar_author_ids.add(author_id)
