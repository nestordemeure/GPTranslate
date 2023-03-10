import abc
from .epub import EpubBook

class Book(abc.ABC):
    """
    Represents a book
    encapsulating its internal (extension dependent) representation
    """

    @abc.abstractmethod
    def __init__(self, path=None, data=None):
        """
        load a book from a given path or ready-made data
        """
        pass
    
    @abc.abstractmethod
    def read_all(self):
        """
        returns a tree representation of the text
        either a root (a list of (string,tree) where the string are equivalent to chapter titles)
        or a leaf (a list of string)
        """
        pass

    @abc.abstractmethod
    def write_all(self, updated_data):
        """
        takes a tree representation of the text
        either a root (a list of (string,tree) where the string are equivalent to chapter titles)
        or a leaf (a list of string)
        
        updates the book in place
        might destroy the tree representation in the process
        """
        pass
    
    @abc.abstractmethod
    def save(self, path):
        """
        saves the book to the given path
        """
        pass