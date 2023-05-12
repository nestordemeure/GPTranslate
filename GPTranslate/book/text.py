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
        with open(path, "r", encoding="utf-8") as file:
            # imports the string
            data = file.read()
            # split at the endline characters
            data = data.splitlines(keepends=True)
            return TextBook(data, path)

    def save(self, path):
        """
        saves the text to the given path
        """
        with open(path, "w", encoding="utf-8") as file:
            file.writelines(self.data)
