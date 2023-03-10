from ebooklib import epub, ITEM_DOCUMENT
from bs4 import BeautifulSoup
from . import Book
from . import html

class EpubBook(Book):
    """
    Represents an epub
    """

    def __init__(self, path):
        """
        load an epub from a given path
        """
        self.data = epub.read_epub(path)

    def _read_all(self):
        """
        returns a dictionary of lists of string, one list per chapter (plus metadata)
        """
        result = list()
        # read metadata
        metadata_list = list()
        for (namespace, metadata) in self.data.metadata.items():
            for (name, data) in metadata.items():
                for (value, other) in data:
                    if isinstance(value, str):
                        metadata_list.append(value)
        result.append(('metadata',metadata_list))
        # read chapters
        for chapter in self.data.get_items_of_type(ITEM_DOCUMENT):
            name = chapter.get_name()
            content = chapter.get_content()
            # parses the html
            html = BeautifulSoup(content, 'html.parser')
            text_list = list()
            for node in html.find_all(string=True):
                if not ((node.parent.name in html.blacklist) or (node.isspace())):
                    text = str(node)
                    if not text.strip().isdigit():
                        text_list.append(text)
            # saving the result
            result.append((name,text_list))
        return result

    def _write_all(self, updated_data):
        """
        takes a dictionary of lists of string, one list per chapter
        and updates the book in place
        """
        updated_data.reverse()
        # write metadata
        metadata_list = updated_text.pop()
        metadata_list.reverse()
        for (namespace, metadata) in self.data.metadata.items():
            for (name, data) in metadata.items():
                updated_metadata = list()
                for (value, other) in data:
                    if isinstance(value, str):
                        updated_value = metadata_list.pop()
                        updated_metadata.append( (updated_value,other) )
                    else:
                        updated_metadata.append( (value,other) )
                metadata[name] = updated_metadata
        # write chapters
        for chapter in self.data.get_items_of_type(ITEM_DOCUMENT):
            # TODO delegate this to an html book format
            name = chapter.get_name()
            content = chapter.get_content()
            text_list = updated_data.pop()
            text_list.reverse()
            # parses the html
            html = BeautifulSoup(content, 'html.parser')
            for node in html.find_all(string=True):
                if not ((node.parent.name in html.blacklist) or (node.isspace())):
                    text = str(node)
                    if not text.strip().isdigit():
                        updated_text = text_list.pop()
                        updated_node = node.replace(text, updated_text)
                        node.replace_with(updated_node)
            # saving the result
            updated_content = html.prettify("utf-8")
            chapter.set_content(updated_content)

    def save(self, path):
        """
        saves the epub to the given path
        """
        epub.write_epub(path, self.data)
