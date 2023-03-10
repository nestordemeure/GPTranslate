from pathlib import Path
from GPTranslate import Book, Translation

#----------------------------------------------------------------------------------------
# PARAMETERS

source_language = 'Russian'
target_language = 'English'
data_folder = Path('./data')
source_file = data_folder / 'Kirill Eskov - the Gospel of Afranius [ru].epub'
target_file = data_folder / 'Kirill Eskov - the Gospel of Afranius [en].epub'
translation_file = data_folder / 'Kirill Eskov - the Gospel of Afranius.trans'
check_translation_manually = False
verbose = True

#----------------------------------------------------------------------------------------
# TRANSLATION

# imports the epub file
print(f"Importing `{source_file}`...")
book = Book.load(source_file)

# translating  the book
print(f"Translating `{source_file}`...")
book.translate(source_language, target_language, translation_file, check_translation_manually, verbose)

# exporting the epub file
print(f"Exporting `{target_file}`...")
book.save(target_file)

print(f"Done!")