import json

def encode_translation(tranlation):
    """takes a translation and build a json around it"""
    return json.dumps({'translation': tranlation})

def decode_malformated_translation(text, source):
    """
    decodes a potentially malformated json
    returns the content of the 'translation' field
    returns the source as is if no translation is offered
    """
    # cut at translation
    translation_markers = '"translation":'
    index_start = text.find(translation_markers)
    if index_start < 0: 
        return source
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
    # remove starting/ending " and ",
    if text.startswith('"'): text = text[1:]
    if text.endswith('"'): text = text[:-1]
    elif text.endswith('",'): text = text[:-2]
    return text

def decode_translation(json_text, source):
    """
    decodes a json
    returns the content of the 'translation' field
    returns the source as is if no translation is offered
    """
    # remove any trailing bit of text
    # (a common type of malformed input)
    last_brace_idx = json_text.rfind('}')
    json_text = json_text[:(last_brace_idx+1)]
    # decode json
    try:
        # use a proper parser
        translation = json.loads(json_text).get('translation', source)
    except Exception as e:
        print(f"JSON: '{e}' for '{json_text}'")
        # use a rougher parser that can deal with malformated inputs
        translation = decode_malformated_translation(json_text, source)
    # cleanup escaped string
    translation = translation.replace('\\"', '"')
    return translation
