class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False

    
class Operations:
    def __init__(self):
        self.root = TrieNode() 
    def insert(self, root, word):
        node = root

        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end_of_word = True
    
    def search(self, word):
        node = self.root

        for ch in word:
            if ch not in node.children:
                return False
            node = node.children[ch]
        # is_end_of_word does not need to be at the leaf, it can be any where, once the iteration over the
        # word ends just send is_end_of_word, if the word was inserted then it will carry True value, else
        # word is just a prefix and is_end_of_word will have default False value in it.
        return node.is_end_of_word
    
    def search_prefix(self, prefix):
        node = self.root

        for ch in prefix:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return True
    
    def delete(self, word):
        node = self.root
        # iterate and go to the end of the branch containing the target word.
        def del_word(node, word, depth):
            if node is None:
                return False
            if len(word) == depth:
                if not node.is_end_of_word:
                    return False
                # even if the ch is not deleted becuase it may have children but still we have to
                # mark is_end_of_word to False because we don't want this word to be found in the search. 
                # trie: cart - delete - car -> we will not delete any node but still mark is_end_of_word
                # for node r, so that car is not found in the search. 
                node.is_end_of_word = False
                if len(node.children) == 0:
                    return True
                else:
                    return False
            ch = word[depth]

            can_delete = del_word(node.children[ch], word, depth+1)
            if can_delete:
                del(node.children[ch])
            
            if len(node.children) == 0 and not node.is_end_of_word:
                return True
            return False 


        return del_word(node, word, 0)