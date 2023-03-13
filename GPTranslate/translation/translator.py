from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import SystemMessagePromptTemplate
from langchain.schema import AIMessage, HumanMessage
from .human_picker import pick_translation
from .json import encode_translation, decode_translation

#----------------------------------------------------------------------------------------
# PARAMETERS

max_history_size = 15
temperature = 0.8

#----------------------------------------------------------------------------------------
# PROMPT

# main prompt
# NOTE: we use the json with notes and success fields to avoid having it comment its own work
template = """I want you to act as a translator from {source_language} to {target_language}.
I will speak to you in {source_language} or English and you will translate in {target_language}.
Your output should be in json format with optional 'translation' (string, only include the translation and nothing else, do not write explanations here), 'notes' (string) and 'success' (boolean) fields.
If an input cannot be translated, return it unmodified."""
system_message_prompt = SystemMessagePromptTemplate.from_template(template)

#----------------------------------------------------------------------------------------
# SET-UP

def reversible_strip(text):
    """returns a stripped text as well as prefix and suffix to rebuild it"""
    prefix = text[:len(text) - len(text.lstrip())]
    suffix = text[len(text.rstrip()):]
    stripped_text = text.strip()
    return stripped_text, prefix, suffix

def build_history(previous_translations, max_history_size):
    """truncates the history (if needed) and strips messages"""
    # truncate history
    if len(previous_translations) > max_history_size:
        previous_translations = previous_translations[(-max_history_size):]
    # strip all messages
    return [ (source.strip(), translation.strip()) for (source,translation) in previous_translations ]

def build_messages(source, source_language, target_language, previous_translations):
    """builds a prompt made of a user message followed by a chat"""
    # build system prompt
    messages = [system_message_prompt.format(**{'source_language':source_language, 'target_language':target_language})]
    # add previous translation
    for (prev_source,prev_translation) in previous_translations:
        human_message = HumanMessage(content=f"Translate:\n\n{prev_source}")
        messages.append(human_message)
        ai_answer = AIMessage(content=encode_translation(prev_translation))
        messages.append(ai_answer)
    # add current message
    human_message = HumanMessage(content=f"Translate:\n\n{source}")
    messages.append(human_message)
    return messages

#----------------------------------------------------------------------------------------
# MODEL

# the model that will be used for the translation
model = ChatOpenAI(temperature=temperature)

def call_model(messages, nb_generations=1):
    """calls the model and returns a list of answers"""
    # generate a batch of inputs (if we need more than one output)
    messages_batch = [messages] * nb_generations
    # runs the model
    answers = model.generate(messages=messages_batch).generations
    answers = [answer[0].text for answer in answers]
    return answers

#----------------------------------------------------------------------------------------
# TRANSLATE

def translate(source, source_language, target_language, previous_translations=[], user_helped=False, verbose=True):
    """takes a string and a list of previous translation in sequential order in order to build a new translation"""
    # prepare inputs
    stripped_source, prefix, suffix = reversible_strip(source)
    previous_translations = build_history(previous_translations, max_history_size)
    messages = build_messages(stripped_source, source_language, target_language, previous_translations)
    nb_generations = 3 if user_helped else 1
    # call the model
    try:
        answers = call_model(messages, nb_generations)
    except Exception as e:
        # too many tokens
        if len(previous_translations) == 0: 
            # we cannot decrease the context
            raise e
        else:
            # restart with a smaller context
            print(f"Warning: '{e}' restarting with {len(previous_translations)} elements.")
            previous_translations = previous_translations[1:]
            return translate(source, source_language, target_language, previous_translations, user_helped, verbose)
    # parses outputs
    translations = [decode_translation(answer, stripped_source) for answer in answers]
    # picks an output
    stripped_translation = pick_translation(stripped_source, translations, previous_translations) if user_helped else translations[0]
    # unstrip
    translation = prefix + stripped_translation + suffix
    return translation