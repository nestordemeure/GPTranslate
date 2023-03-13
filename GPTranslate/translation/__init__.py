import pickle
import asyncio
from .translator import translate

#------------------------------------------------------------------------------
# TEXT PROCESSONG

def contains_text(text):
    """returns True if this is a string containing some text"""
    return (isinstance(text, str) or isinstance(text, bytes)) and any(c.isalpha() for c in text)

#------------------------------------------------------------------------------
# TREE PROCESSING

def is_leaf(tree):
    """returns true if a tree is a leaf"""
    return (len(tree) > 0) and not isinstance(tree[0], tuple)

def empty_clone(tree):
    """clones a tree, replacing leaves with empty lists"""
    if is_leaf(tree):
        return list()
    else:
        return [ (name,empty_clone(child)) for (name,child) in tree ]

def tree_equal(tree1, tree2):
    """returns True if both trees are exactly equal"""
    if (len(tree1) != len(tree2)) or (is_leaf(tree1) != is_leaf(tree2)):
        # False if nodes have different structures
        return False
    elif is_leaf(tree1):
        # leaf, check values
        return tree1 == tree2
    else:
        # node, check for the equality of all subtrees
        for ((name1,child1), (name2,child2)) in zip(tree1,tree2):
            if not ((name1 == name2) and tree_equal(child1,child2)):
                return False
        return True

#------------------------------------------------------------------------------
# TRANSLATION

class Translation:
    """
    represent a translation being performed
    intermediate results will automatically be saved in `autosave_path`
    """

    def __init__(self, data, language_source, language_target, autosave_path=None):
        self.source = data
        self.translation = empty_clone(data)
        self.language_source = language_source
        self.language_target = language_target
        self.autosave_path = autosave_path

    def _translate_serial(self, name, source, translation, user_helped=False, verbose=False):
        """goes through the tree serialy and performs the translation"""
        # process down the tree recurcively
        if is_leaf(source):
            # this is a leaf node
            # pick up where we were
            nb_done = len(translation)
            sources_done = source[:nb_done]
            sources_todo = source[nb_done:]
            history = list(zip(sources_done, translation))
            # go through text left
            for i,text in enumerate(sources_todo):
                if verbose: print(f"{name} {1+i+nb_done}/{len(source)}")
                if contains_text(text):
                    translated_text = translate(text, self.language_source, self.language_target, history, user_helped=user_helped, verbose=verbose)
                    history.append((text,translated_text))
                else:
                    # skip text that does not contain letters
                    translated_text = text
                translation.append(translated_text)
                # autosave at every translation when user_helped is activated
                if user_helped and (self.autosave_path is not None): self.save(self.autosave_path)
            # autosave at the end of every leaf
            if self.autosave_path is not None: self.save(self.autosave_path)
            if verbose: print(f"{name} done.")
        else:
            # this is a root node
            # process all children
            for ((name_child,source_child),(_,translation_child)) in zip(source, translation):
                self._translate_serial(f"{name}|{name_child}", source_child, translation_child, user_helped=user_helped, verbose=verbose)

    async def _translate_async(self, name, source, translation, verbose=False):
        """goes through the tree asynchronously and perform the translation"""
        # process down the tree recurcively
        if is_leaf(source):
            # this is a leaf node
            await asyncio.to_thread(self._translate_serial, name, source, translation, verbose=verbose)
        else:
            # this is a root node
            # process all children
            tasks = list()
            for ((name_child,source_child),(_,translation_child)) in zip(source, translation):
                task_child = self._translate_async(f"{name}|{name_child}", source_child, translation_child, verbose=verbose)
                tasks.append(task_child)
            # wait on all the tasks
            await asyncio.gather(*tasks)

    def _translate_parallel(self, name, source, translation, verbose=False):
        """goes through the tree asynchronously and perform the translation"""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._translate_async(name, source, translation, verbose=verbose))

    def translate(self, user_helped=False, verbose=False):
        """performs the translation"""
        # check if a translation is already underway
        if (self.autosave_path is not None) and self.autosave_path.exists():
            previous_translation = Translation.load(self.autosave_path)
            if (previous_translation.language_source == self.language_source) and (previous_translation.language_target == self.language_target) and tree_equal(previous_translation.source,self.source):
                print(f"Loading '{self.autosave_path}' partial translation.")
                self.translation = previous_translation.translation
        # performs the translation
        if user_helped:
            self._translate_serial(name='', source=self.source, translation=self.translation, user_helped=False, verbose=verbose)
        else:
            self._translate_parallel(name='', source=self.source, translation=self.translation, verbose=verbose)
        # delete the autosaved file
        if (self.autosave_path is not None) and self.autosave_path.exists():
            self.autosave_path.unlink()
        return self.translation

    def save(self, path):
        """save the translation to disk"""
        with open(path, 'wb') as f:
            pickle.dump(self, f)
    
    @staticmethod
    def load(path) -> 'Translation':
        """loads the translation from disk"""
        with open(path, 'rb') as f:
            obj = pickle.load(f)
        return obj