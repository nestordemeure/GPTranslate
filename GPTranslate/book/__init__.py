import abc
from pathlib import Path
from ..translation import Translation

class Book(abc.ABC):
    """
    Represents a book
    encapsulating its internal (extension dependent) representation
    """

    def __init__(self, data):
        """
        load a book from given ready-made data
        """
        self.data = data
    
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
        #translation = Translation(texts, language_source, language_target)
        #texts_updated = translation.translate(autosave_path, user_helped, verbose)
        texts_updated = texts # TODO
        if verbose: print("Updating book...")
        self._import_raw_texts(texts_updated)

    @staticmethod
    def load(path: Path) -> 'Book':
        """
        loads a book from a given path
        """
        # NOTE does the import inside the function to avoid circular dependencies
        extension = path.suffix
        if extension == '.epub':
            from .epub import EpubBook
            return EpubBook.load(path)
        elif extension in ['.html', '.xhtml']:
            from .html import HtmlBook
            return HtmlBook.load(path)
        else:
            raise ValueError(f"Unsupported extension: {extension}")

    @abc.abstractmethod
    def save(self, path):
        """
        saves the book to the given path
        """
        pass