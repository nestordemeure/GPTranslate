import re
from io import StringIO
from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams
from .text import TextBook

class PdfBook(TextBook):
    """
    Represents a pdf as a text
    note that we lose the formating but it seems like the best compromise achieveable for now
    """
    def load(path):
        """
        loads the text from a given path
        """
        with open(path, 'rb') as file: 
            # parse the pdf into a text file
            data = extract_text(file, laparams=LAParams())
            # split at the endline characters
            data = data.splitlines()
            return PdfBook(data, path)

    def save(self, path):
        """
        saves the text to the given path
        """
        # insures that the output is a html file
        path = path.with_suffix('.txt')
        # saves
        with open(path, "w") as file:
            data = [(line + '\n') for line in self.data]
            file.writelines(data)
