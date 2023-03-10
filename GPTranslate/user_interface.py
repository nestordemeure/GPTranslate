import os

def clear_shell():
    """Clears the shell screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def pick_translation(source, translations, previous_translations):
    """
    takes a source to translate
    several alternative translations
    and the translations of the previous parts of the text
    returns a user picked or written translation
    """
    clear_shell()
    # displays the context
    if len(previous_translations) > 0:
        print(f"CONTEXT:")
        for (previous_source,previous_translation) in previous_translations:
            print(previous_translation)
    # displays the source
    print("\nSOURCE (TRANSLATION 0):")
    print(source)
    # displays the translation
    translations = list(set(translations)) # keeps only unique translations
    for (i,translation) in enumerate(translations):
        print(f"\nTRANSLATION {i+1}:")
        print(translation)
    # display the instructions
    print()
    if len(translations) > 1:
        print("Press Enter to pick translation 1.")
        print("Type a number to pick a given translation.")
    else:
        print("Press Enter to pick the translation.")
    print("Otherwise, type your own translation:")
    print()
    # process user input
    user_input = input("Translation: ")
    if len(user_input) == 0:
        print("\nUsing the first translation.\n")
        return translations[0]
    elif user_input.isdigit():
        i = int(user_input)-1
        if i < 0:
            print(f"\nUsing original text.\n")
            return source
        elif i < len(translations):
            print(f"\nUsing {i+1}th translation.\n")
            return translations[i]
        else:
            return pick_translation(previous_translations, source, translations)
    else:
        print("\nUsing manual translation.\n")
        return user_input