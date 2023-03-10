from bs4 import BeautifulSoup
from . import Book

# node types that should not be considered text
non_text_section = ['[document]','noscript','header','html','meta','head','input','script']

class HtmlBook(Book):
    """
    Represents an html as a single string
    (for ease of interoperability with epub format)
    """
    def _export_raw_texts(self):
        """
        reads all text nodes
        """
        # TODO split on headers
        texts_list = list()
        # parses the html
        html = BeautifulSoup(self.data, 'html.parser')
        for node in html.find_all(string=True):
            if not ((node.parent.name in non_text_section) or (node.isspace())):
                text = str(node)
                if not text.strip().isdigit():
                    texts_list.append(text)
        return texts_list

    def _import_raw_texts(self, texts_list):
        """
        updates all text nodes
        """
        # TODO split on headers
        texts_list.reverse()
        # parses the html
        html = BeautifulSoup(self.data, 'html.parser')
        for node in html.find_all(string=True):
            if not ((node.parent.name in non_text_section) or (node.isspace())):
                text = str(node)
                if not text.strip().isdigit():
                    updated_text = texts_list.pop()
                    updated_node = node.replace(text, updated_text)
                    node.replace_with(updated_node)
        # saving the result
        self.data = html.prettify("utf-8")

    def load(path):
        """
        loads the html from a given path
        """
        with open(path, "r") as file:
            data = file.read()
            return HtmlBook(data)

    def save(self, path):
        """
        saves the htlm to the given path
        """
        with open(path, "w") as file:
            file.write(self.data)
