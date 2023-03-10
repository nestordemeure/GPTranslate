from ebooklib import epub, ITEM_DOCUMENT
from . import Book
from .html import HtmlBook

class EpubBook(Book):
    """
    Represents an epub
    """
    def _export_raw_texts(self):
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
            # parsing the html
            html = HtmlBook(content)
            text_list = html._export_raw_texts()
            # saving the result
            result.append((name,text_list))
        return result

    def _import_raw_texts(self, updated_data):
        """
        takes a dictionary of lists of string, one list per chapter
        and updates the book in place
        """
        updated_data.reverse()
        # write metadata
        name, metadata_list = updated_data.pop()
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
            content = chapter.get_content()
            (name,texts_list) = updated_data.pop()
            # parsing the html
            html = HtmlBook(content)
            html._import_raw_texts(texts_list)
            # saving the result
            updated_content = html.data
            chapter.set_content(updated_content)

    def load(path):
        """
        loads the epub from a given path
        """
        data = epub.read_epub(path)
        return EpubBook(data)

    def save(self, path):
        """
        saves the epub to the given path
        """
        epub.write_epub(path, self.data)
