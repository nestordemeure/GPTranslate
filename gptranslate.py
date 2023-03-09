from pathlib import Path
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from bs4.element import NavigableString
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

#----------------------------------------------------------------------------------------
# PARAMETERS

# files
source_language = 'Russian'
target_language = 'English'
data_folder = Path('./data')
source_file = data_folder / 'Kirill Eskov - Déjà vu [ru].epub'
target_file = data_folder / 'Kirill Eskov - Déjà vu [en].epub'

# translation
verbose = True
max_history_size = 15

#----------------------------------------------------------------------------------------
# TRANSLATION

# the model that will be used for the translation
model = ChatOpenAI(temperature=0.0)

# main prompt
system_message = f"Translate from {source_language} to {target_language}. \
Your output should be in json format with optional 'translation' (string), 'notes' (string) and 'success' (boolean) fields. \
If an input cannot be translated, return it unmodified."

# main prompt
system_message = f"I want you to act as a translator from {source_language} to {target_language}. \
I will speak to you in {source_language} or English and you will translate it and answer in {target_language}. \
Your output should be in json format with optional 'translation' (string), 'notes' (string) and 'success' (boolean) fields. \
If an input cannot be translated, return it unmodified."

def answer_to_json(text):
    """takes a text and builds a dummy json from it"""
    return '{"translation": "' + text + '"}'

def json_to_answer(text, alternative_result):
    """
    takes a roughly json formated string
    extracts the 'translation' field
    using the other fields and braces as markers
    we are purposefully not using a proper parser as the json could be malformated in ways no parsers accept
    """
    # cut at translation
    translation_markers = '"translation":'
    index_start = text.find(translation_markers)
    if index_start < 0: 
        return alternative_result
    else:
        index_start += len(translation_markers)
        text = text[index_start:].strip()
    # find the end marker that is closest to the beginning
    index_end = len(text)
    notes_marker = '"notes":'
    index_notes = text.rfind(notes_marker)
    if (index_notes >= 0) and (index_notes < index_end): index_end = index_notes
    success_markers = '"success":'
    index_success = text.rfind(success_markers)
    if (index_success >= 0) and (index_success < index_end): index_end = index_success
    brace_marker = '}'
    index_brace = text.rfind(brace_marker)
    if (index_brace >= 0) and (index_brace < index_end): index_end = index_brace
    # cut on the marker
    text = text[:index_end].strip()
    # remove " and ",
    if text.startswith('"'): text = text[1:]
    if text.endswith('"'): text = text[:-1]
    elif text.endswith('",'): text = text[:-2]
    # clean up escaped string
    text = text.replace('\"', '"')
    text = text.replace('\"', '"') # slitly different encoding
    print(f"ANSWER: '{text}'")
    return text

def translate(text, previous_translation=[], verbose=True):
    """takes a string and a list of previous translation in sequential order in order to build a new translation"""
    # truncate history
    if len(previous_translation) > max_history_size:
        previous_translation = previous_translation[(-max_history_size):]
    # build a list of messages
    messages = [SystemMessage(content=system_message)]
    for (source,translation) in previous_translation:
        human_message = HumanMessage(content=f"Translate:\n\n{source}")
        messages.append(human_message)
        ai_answer = AIMessage(content=answer_to_json(translation))
        messages.append(ai_answer)
    human_message = HumanMessage(content=f"Translate:\n\n{text}")
    messages.append(human_message)
    # generate answer
    try:
        answer = model(messages).content
    except Exception as e:
        # restart if the context is too large causing errors
        if len(previous_translation) == 0: raise e
        previous_translation.pop()
        print(f"ERROR: '{e}' restarting with {len(previous_translation)} elements.")
        return translate(text, previous_translation=previous_translation, verbose=verbose)
    # parse answer
    translation = json_to_answer(answer, text)
    return translation

def translate_html(html, verbose=False):
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
    # intermediate save for debug purposes
    if verbose: epub.write_epub(target_file, book)

# exports the translated file
print(f"Exporting `{target_file}`...")
epub.write_epub(target_file, book)

print(f"Done!")