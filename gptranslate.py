from pathlib import Path
from GPTranslate import Book, Translation

#----------------------------------------------------------------------------------------
# PARAMETERS

language_source = 'Russian'
language_target = 'English'
data_folder = Path('./data')
source_file = data_folder / 'Kirill Eskov - the Gospel of Afranius [ru].epub'
target_file = data_folder / 'Kirill Eskov - the Gospel of Afranius [en].epub'
translation_file = data_folder / 'Kirill Eskov - the Gospel of Afranius.trans'
check_translation_manually = False
verbose = True

language_source = 'English'
language_target = 'French'
source_file = data_folder / 'test [en].html'
target_file = data_folder / 'test [fr].html'
translation_file = data_folder / 'test.trans'
check_translation_manually = False
verbose = True

language_source = 'English'
language_target = 'French'
source_file = data_folder / 'test [en].pdf'
target_file = data_folder / 'test [fr].pdf'
translation_file = data_folder / 'test.trans'
check_translation_manually = False
verbose = True

#----------------------------------------------------------------------------------------
# TRANSLATION

# imports the epub file
print(f"Importing `{source_file}`...")
book = Book.load(source_file)

# translating  the book
print(f"Translating `{source_file}`...")
book.translate(language_source, language_target, translation_file, check_translation_manually, verbose)

# exporting the epub file
print(f"Exporting `{target_file}`...")
book.save(target_file)

print(f"Done!")