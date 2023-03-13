"""
    Splits leaves into overlapping blocks to be processed in parallel
    This is significantly faster
    but also costlier (due to the overlap)
    and less accurate (text following overlapping sections is more likely to be less coherent with the rest of the text)
"""
from .tree_processing import contains_text

# maximum size of blocks after slicing leaves
block_size = 60
# overlap between blocks
overlap = 10

def should_slice(source):
    actual_block_size = 0
    for txt in source:
        if contains_text(txt):
            actual_block_size += 1
            if actual_block_size > block_size+2*overlap:
                return True
    return False

def slice_leaf(source, translation):
    sources = list()
    translations = list()
    overlaps = [0]
    current_source = list()
    current_translation = list()
    current_source_size = 0
    next_source = list()
    next_translation = list()
    next_source_size = 0
    for i,txt in enumerate(source):
        # saves the data
        has_text = contains_text(txt)
        has_translation = (i < len(translation))
        current_source.append(txt)
        if has_translation: current_translation.append(txt)
        if has_text: current_source_size += 1
        # we are in an overlapping section
        if current_source_size > block_size-overlap:
            next_source.append(txt)
            if has_translation: next_translation.append(txt)
            if has_text: next_source_size += 1
        # go to the next slice
        if current_source_size >= block_size:
            sources.append(current_source)
            translations.append(current_translation)
            overlaps.append(next_source_size)
            current_source = next_source
            current_translation = next_translation
            current_source_size = next_source_size
            next_source = list()
            next_translation = list()
            next_source_size = 0
    # add leftover
    if len(current_source) > 0: 
        sources.append(current_source)
        translations.append(current_translation)
        overlaps.append(next_source_size)
    if len(next_source) > 0: 
        sources.append(next_source)
        translations.append(next_translation)
        overlaps.append(0)
    return sources, translations, overlaps

def unslice_leaf(translations, overlaps):
    result = list()
    for (translation,overlap_index) in zip(translations,overlaps):
        slice_translations = translation[overlap_index:]
        result.extend(slice_translations)
    return result