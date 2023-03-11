from bs4 import BeautifulSoup
from . import Book

# node types that should not be considered text
non_text_section = ['[document]','noscript','header','html','meta','head','input','script']

def is_heading(node):
    """returns True is a node descends form a heading"""
    for parent in node.find_parents():
        if parent.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            return True
    return False

class HtmlBook(Book):
    """
    Represents an html as a single string
    (for ease of interoperability with epub format)
    """
    def _export_raw_texts(self):
        """
        reads all text nodes
        """
        # we will have one list per heading
        result = list()
        heading_name = 'root'
        texts_list = list()
        # parses the html
        html = BeautifulSoup(self.data, 'html.parser')
        for node in html.find_all(string=True):
            if not ((node.parent.name in non_text_section) or (node.isspace())):
                text = str(node)
                if is_heading(node):
                    result.append((heading_name,texts_list))
                    heading_name = text.strip()
                    texts_list = list()
                if not text.strip().isdigit():
                    texts_list.append(text)
        # adds the very last section and returns
        result.append((heading_name,texts_list))
        return result

    def _import_raw_texts(self, result):
        """
        updates all text nodes
        """
        # we will have one list per heading
        result.reverse()
        heading_name, texts_list = result.pop()
        texts_list.reverse()
        # parses the html
        html = BeautifulSoup(self.data, 'html.parser')
        for node in html.find_all(string=True):
            if not ((node.parent.name in non_text_section) or (node.isspace())):
                text = str(node)
                if is_heading(node):
                    heading_name, texts_list = result.pop()
                    texts_list.reverse()
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
        with open(path, 'rb') as file:
            data = file.read()
            return HtmlBook(data)

    def save(self, path):
        """
        saves the htlm to the given path
        """
        with open(path, 'wb') as file:
            file.write(self.data)
