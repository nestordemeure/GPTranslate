from . import Book

class TextBook(Book):
    """
    Represents a text as a list of strings
    """
    def _export_raw_texts(self):
        return self.data

    def _import_raw_texts(self, texts_list):
        self.data = texts_list

    def load(path):
        """
        loads the text from a given path
        """
        with open(path, "r") as file:
            data = [line.strip() for line in file.readlines()]
            return TextBook(data)

    def save(self, path):
        """
        saves the text to the given path
        """
        with open(path, "w") as file:
            data = [(line + '\n') for line in self.data]
            file.writelines(data)
