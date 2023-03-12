import re
from io import StringIO
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
from .html import HtmlBook

class PdfBook(HtmlBook):
    """
    Represents a pdf as an html
    note that we lose some of the formating but it seems like the best compromise achieveable for now
    """
    def load(path):
        """
        loads the text from a given path
        """
        with open(path, 'rb') as file: 
            # parse the pdf into a html
            buffer = StringIO()
            extract_text_to_fp(file, buffer, laparams=LAParams(), output_type='html', codec=None)
            data = buffer.getvalue()
            # turn pages into heading so that the html parser will split there
            data = re.sub(r'<a name="(\d+)">Page (\d+)</a>', r'<h5 name="\1">Page \2</h5>', data)
            # save the text
            return PdfBook(data, path)

    def save(self, path):
        """
        saves the text to the given path
        """
        # insures that the output is a byte encoded html file
        path = path.with_suffix('.html')
        self.data = self.data.encode('utf-8')
        # saves
        with open(path, 'wb') as file:
            file.write(self.data)
