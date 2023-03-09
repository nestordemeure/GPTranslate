from pathlib import Path
from ebooklib import epub
from GPTranslate import translate_book

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

# imports the epub file
print(f"Importing `{source_file}`...")
book = epub.read_epub(source_file)

# translating  the book
print(f"translating `{source_file}`...")
book = translate_book(book, source_language=source_language, target_language=target_language, 
                      output_file=target_file, verbose=verbose)

# exporting the epub file
epub.write_epub(target_file, book)
print(f"Done!")