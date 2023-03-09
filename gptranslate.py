from pathlib import Path
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from bs4.element import NavigableString

#----------------------------------------------------------------------------------------
# PARAMETERS

source_language = 'Russian'
target_language = 'English'
data_folder = Path('./data')
source_file = data_folder / 'Kirill Eskov - Déjà vu [ru].epub'
target_file = data_folder / 'Kirill Eskov - Déjà vu [en].epub'
verbose = True

#----------------------------------------------------------------------------------------
# TRANSLATION

def translate(text, previous_translation=[]):
    """takes a string and a list of previous translation in sequential order in order to build a new translation"""
    # TODO dummy function
    return f"[{source_language}->{target_language}]{text}"

def translate_html(html, verbose=False):
    """takes a string representation of an html and translates its text components"""
    # parse the html
    html = BeautifulSoup(html, 'html.parser')
    # extracts all of the text nodes
    blacklist = ['[document]','noscript','header','html','meta','head','input','script']
    text_nodes = [text for text in html.find_all(string=True) if not ((text.parent.name in blacklist) or (text.isspace()))]
    # translate the text node one at a time
    previous_translations = []
    for i,text_node in enumerate(text_nodes):
        # displays the progress
        if verbose: print(f" * {i+1}/{len(text_nodes)}")
        # performs the translation
        text = str(text_node)
        translated_text = translate(text, previous_translations)
        previous_translations.append((text, translated_text))
        # updates the node
        translated_text_node = text_node.replace(text, translated_text)
        text_node.replace_with(translated_text_node)
    # turn back into a string
    return html.prettify("utf-8")

#----------------------------------------------------------------------------------------
# PROCESSING

# imports the epub file
print(f"Importing `{source_file}`...")
book = epub.read_epub(source_file)

# translates the metadata
print(f"Translating metadata...")
nb_metadata = 0
for (namespace, metadata) in book.metadata.items():
    for (name, data) in metadata.items():
        translated_data = []
        for (value, other) in data:
            # displays the progress
            nb_metadata += 1
            if verbose: print(f" * {nb_metadata}")
            # translates the value
            translated_value = translate(value)
            translated_data.append( (translated_value,other) )
        metadata[name] = translated_data

# process all of the html chapters
chapters = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
for i,chapter in enumerate(chapters):
    print(f"Translating chapter `{chapter.get_name()}` ({i+1}/{len(chapters)})...")
    content = chapter.get_content()
    translated_content = translate_html(content, verbose)
    chapter.set_content(translated_content)

# exports the translated file
print(f"Exporting `{target_file}`...")
epub.write_epub(target_file, book)

print(f"Done!")