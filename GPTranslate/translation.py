from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import SystemMessagePromptTemplate
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
from .user_interface import pick_translation

#----------------------------------------------------------------------------------------
# PARAMETERS

max_history_size = 15
temperature = 0.9

#----------------------------------------------------------------------------------------
# JSON HANDLING

def answer_to_json(translation):
    """takes a translation and builds a dummy json from it"""
    return '{"translation": "' + translation + '"}'

def json_to_answer(text, alternative_result, verbose=False):
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
    #if verbose: print(f"\n{text}\n")
    return text

#----------------------------------------------------------------------------------------
# PROMPT AND MODEL

# the model that will be used for the translation
model = ChatOpenAI(temperature=temperature)

# main prompt
template = """I want you to act as a translator from {source_language} to {target_language}.
I will speak to you in {source_language} or English and you will translate in {target_language}.
Your output should be in json format with optional 'translation' (string, only include the translation and nothing else, do not write explanations here), 'notes' (string) and 'success' (boolean) fields.
If an input cannot be translated, return it unmodified."""
system_message_prompt = SystemMessagePromptTemplate.from_template(template)

#----------------------------------------------------------------------------------------
# TRANSLATE

def translate(text, source_language, target_language, previous_translations=[], user_helped=False, verbose=True):
    """takes a string and a list of previous translation in sequential order in order to build a new translation"""
    # truncate history
    if len(previous_translations) > max_history_size:
        previous_translations = previous_translations[(-max_history_size):]
    # build a list of messages
    messages = [system_message_prompt.format(**{'source_language':source_language, 'target_language':target_language})]
    for (source,translation) in previous_translations:
        human_message = HumanMessage(content=f"Translate:\n\n{source}")
        messages.append(human_message)
        ai_answer = AIMessage(content=answer_to_json(translation))
        messages.append(ai_answer)
    human_message = HumanMessage(content=f"Translate:\n\n{text}")
    messages.append(human_message)
    # generate answer
    try:
        # generate a batch of inputs (if needed)
        nb_generations = 3 if user_helped else 1
        messages_batch = [messages] * nb_generations
        # runs the model and parses the outputs
        answers = model.generate(messages=messages_batch).generations
        answers = [answer[0].text for answer in answers]
        translations = [json_to_answer(answer, text, verbose=verbose) for answer in answers]
        # picks an output
        translation = pick_translation(text, translations, previous_translations) if user_helped else answers[0]
        return translation
    except Exception as e:
        # restart if the context is too large causing errors
        if len(previous_translations) == 0: raise e
        previous_translations.pop()
        print(f"Warning: '{e}' restarting with {len(previous_translations)} elements.")
        return translate(text, source_language, target_language, previous_translations=previous_translations, verbose=verbose)
