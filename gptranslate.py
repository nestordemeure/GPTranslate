from pathlib import Path
from ebooklib import epub
from GPTranslate import translate_book, translate_book_parallel

#----------------------------------------------------------------------------------------
# PARAMETERS

source_language = 'Russian'
target_language = 'English'
data_folder = Path('./data')
source_file = data_folder / 'Kirill Eskov - the Gospel of Afranius [ru].epub'
target_file = data_folder / 'Kirill Eskov - the Gospel of Afranius [en].epub'
user_aided_translation = True
verbose = True

#----------------------------------------------------------------------------------------
# TRANSLATION

# imports the epub file
print(f"Importing `{source_file}`...")
book = epub.read_epub(source_file)

# translating  the book
print(f"Translating `{source_file}`...")
if user_aided_translation:
    book = translate_book(book, source_language=source_language, target_language=target_language, 
                          output_file=target_file, user_helped=True, verbose=verbose)
else:
    book = translate_book_parallel(book, source_language=source_language, target_language=target_language, 
                                   verbose=verbose)

# exporting the epub file
print(f"Exporting `{target_file}`...")
epub.write_epub(target_file, book)
print(f"Done!")