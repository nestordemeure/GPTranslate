from pathlib import Path
from GPTranslate import Book, Translation

#----------------------------------------------------------------------------------------
# PARAMETERS

language_source = 'auto'
language_target = 'English'
data_folder = Path('./data')
source_file = data_folder / 'Kirill Eskov - the Gospel of Afranius [ru].epub'
target_file = data_folder / 'Kirill Eskov - the Gospel of Afranius [en].epub'
check_translation_manually = True
verbose = True

#----------------------------------------------------------------------------------------
# TRANSLATION

# imports the epub file
print(f"Importing `{source_file}`...")
book = Book.load(source_file)

# translating  the book
print(f"Translating `{source_file}`...")
book.translate(language_source, language_target, user_helped=check_translation_manually, verbose=verbose)

# exporting the epub file
print(f"Exporting `{target_file}`...")
book.save(target_file)

print(f"Done!")