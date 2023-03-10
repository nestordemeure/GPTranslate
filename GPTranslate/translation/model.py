from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import SystemMessagePromptTemplate
from langchain.schema import AIMessage, HumanMessage
from .user_interface import pick_translation
from .json import answer_to_json, json_to_answer

#----------------------------------------------------------------------------------------
# PARAMETERS

max_history_size = 15
temperature = 0.9

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
        translations = [json_to_answer(answer, text) for answer in answers]
        # picks an output
        translation = pick_translation(text, translations, previous_translations) if user_helped else translations[0]
        return translation
    except Exception as e:
        # restart if the context is too large causing errors
        if len(previous_translations) == 0: raise e
        previous_translations.pop()
        print(f"Warning: '{e}' restarting with {len(previous_translations)} elements.")
        return translate(text, source_language, target_language, previous_translations=previous_translations, verbose=verbose)
