import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from bs4.element import NavigableString

from .translation import translate

def translate_html(html, source_language, target_language, verbose=False):
    """takes a string representation of an html and translates its text components"""
    # parse the html
    html = BeautifulSoup(html, 'html.parser')
    # extracts all of the text nodes
    blacklist = ['[document]','noscript','header','html','meta','head','input','script']
    text_nodes = [text for text in html.find_all(string=True) if not ((text.parent.name in blacklist) or (text.isspace()))]
    # translate the text node one at a time
    previous_translations = []
    text_node: NavigableString # type hint
    for i,text_node in enumerate(text_nodes):
        if verbose: print(f" * {i+1}/{len(text_nodes)}")
        text = str(text_node)
        if not text.strip().isdigit():
            # performs the translation
            translated_text = translate(text, source_language, target_language, 
                                        previous_translations=previous_translations, verbose=verbose)
            previous_translations.append((text, translated_text))
            # updates the node
            translated_text_node = text_node.replace(text, translated_text)
            text_node.replace_with(translated_text_node)
    # turn back into a string
    return html.prettify("utf-8")

def translate_metadata(metadata, source_language, target_language, verbose=False):
    """
    takes a dict representation of the metadata and translate its components
    modifications will be done in place
    """
    if verbose: print(f"Translating metadata...")
    nb_metadata = 0
    for (namespace, metadata) in metadata.items():
        for (name, data) in metadata.items():
            translated_data = []
            for (value, other) in data:
                # displays the progress
                nb_metadata += 1
                if verbose: print(f" * {nb_metadata}")
                # translates the value
                translated_value = translate(value, source_language, target_language, verbose=verbose)
                translated_data.append( (translated_value,other) )
            metadata[name] = translated_data
    return metadata

def translate_book(book, source_language, target_language, output_file=None, verbose=False):
    """
    takes a book and translate it
    modifying it in place
    if you pass it `output_file`, it will save after each chapter translation
    """
    # translating the metadata
    translate_metadata(book.metadata, source_language, target_language, verbose=verbose)
    # translating the chapters
    chapters = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
    for i,chapter in enumerate(chapters):
        if verbose: print(f"Translating chapter `{chapter.get_name()}` ({i+1}/{len(chapters)})...")
        content = chapter.get_content()
        translated_content = translate_html(content, source_language, target_language, verbose=verbose)
        chapter.set_content(translated_content)
        # save intermediate result
        if output_file is not None: epub.write_epub(output_file, book)
    return book
