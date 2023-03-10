import abc
from .epub import EpubBook
from .html import HtmlBook
from ..translation import Translation

class Book(abc.ABC):
    """
    Represents a book
    encapsulating its internal (extension dependent) representation
    """

    @abc.abstractmethod
    def __init__(self, data):
        """
        load a book from given ready-made data
        """
        pass
    
    @abc.abstractmethod
    def _export_raw_texts(self):
        """
        returns a tree representation of the text
        either a root (a list of (string,tree) where the string are equivalent to chapter titles)
        or a leaf (a list of string)
        """
        pass

    @abc.abstractmethod
    def _import_raw_texts(self, updated_data):
        """
        takes a tree representation of the text
        either a root (a list of (string,tree) where the string are equivalent to chapter titles)
        or a leaf (a list of string)
        
        updates the book in place
        might destroy the tree representation in the process
        """
        pass
    
    def translate(self, language_source, language_target, autosave_path=None, user_helped=False, verbose=False):
        """translate the text"""
        if verbose: print("Extracting texts from book...")
        texts = self._export_raw_texts()
        if verbose: print("Translating...")
        translation = Translation(texts, language_source, language_target)
        texts_updated = translation.translate(autosave_path, user_helped, verbose)
        if verbose: print("Updating book...")
        self._import_raw_texts(texts_updated)

    @staticmethod
    def load(path) -> 'Book':
        """
        loads a book from a given path
        """
        if path.endswith('.epub'):
            return EpubBook.load(path)
        elif path.endswith('.html') or path.endswith('.xhtml'):
            return HtmlBook.load(path)
        else:
            raise ValueError('Unsupported format.')

    @abc.abstractmethod
    def save(self, path):
        """
        saves the book to the given path
        """
        pass