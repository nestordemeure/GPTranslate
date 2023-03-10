
def answer_to_json(translation):
    """takes a translation and builds a dummy json from it"""
    return '{"translation": "' + translation + '"}'

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
    # cleanup escaped string
    text = text.replace('\\"', '"')
    return text
