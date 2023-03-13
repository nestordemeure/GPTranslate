
def contains_text(text):
    """returns True if this is a string containing some text"""
    return (isinstance(text, str) or isinstance(text, bytes)) and any(c.isalpha() for c in text)

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

def flatten(tree):
    """turns a tree into a single piece of text"""
    if is_leaf(tree):
        result = ""
        for txt in tree:
            if contains_text(txt):
                result += txt
                result += '\n'
        return result
    else:
        result = ""
        for (name,child) in tree:
            result += flatten(child)
        return result
