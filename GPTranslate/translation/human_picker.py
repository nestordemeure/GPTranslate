import os

def clear_shell():
    """Clears the shell screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def pick_translation(source, translations, previous_translations, use_heuristics=True):
    """
    takes a source to translate
    several alternative translations
    and the translations of the previous parts of the text
    returns a user picked or written translation

    NOTE: two heuristics can be used to speed-up the work:
    - if the source is one of the translations then it can be kept (as it likely means that the source is in the target language)
    - if all translations are identical then the result can be returned (as it likely means that the translation is obvious)
    """
    # apply heuristics
    translations = list(set(translations)) # keeps only unique translations
    if use_heuristics:
        if source in translations:
            # likely means that the source is already in the target language
            return source
        elif len(translations) == 1:
            # likely means that the translation is obvious
            return translations[0]
    # displays the context
    clear_shell()
    if len(previous_translations) > 0:
        print(f"CONTEXT:")
        for (prev_source,prev_translation) in previous_translations:
            print(prev_translation)
    # displays the source
    print("\nSOURCE (TRANSLATION 0):")
    print(source)
    # displays the translation
    for (i,translation) in enumerate(translations):
        print(f"\nTRANSLATION {i+1}:")
        print(translation)
    # display the instructions
    print()
    print("Press Enter to pick translation 1.")
    print("Type a number to pick another translation (including the source).")
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
