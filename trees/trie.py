class TrieNode:
    def __init__(self):
        # Maps a character (e.g., 'a') to its corresponding child TrieNode
        self.children = {}
        # Flag to indicate if a complete word ends at this specific node
        self.is_end_of_word = False


class Trie:
    def __init__(self):
        """Initializes the Trie with a blank root node."""
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        """
        Inserts a word into the trie.
        Time Complexity: O(m), where m is the length of the word.
        """
        if not word:
            return

        current = self.root
        for char in word:
            # If the character path doesn't exist, build a new node
            if char not in current.children:
                current.children[char] = TrieNode()
            # Step down into the child node
            current = current.children[char]
        
        # Mark the final node as the completion of a valid word
        current.is_end_of_word = True

    def search(self, word: str) -> bool:
        """
        Returns True if the exact word exists in the trie.
        Time Complexity: O(m)
        """
        if not word:
            return False

        current = self.root
        for char in word:
            if char not in current.children:
                return False
            current = current.children[char]
        
        # It's only a match if the character sequence terminates a full word
        return current.is_end_of_word

    def starts_with(self, prefix: str) -> bool:
        """
        Returns True if there is any word in the trie that starts with the given prefix.
        Time Complexity: O(p), where p is the length of the prefix.
        """
        if not prefix:
            return False

        current = self.root
        for char in prefix:
            if char not in current.children:
                return False
            current = current.children[char]
        
        # If we successfully traced the prefix, at least one word shares it
        return True
    

if __name__ == "__main__":
    # Initialize our Trie
    auto_complete_trie = Trie()

    # Insert sample words
    words = ["apple", "app", "apricot", "banana", "bat"]
    for word in words:
        auto_complete_trie.insert(word)

    # ---- Test Cases ----

    # 1. Exact matches
    print(auto_complete_trie.search("apple"))   # Output: True
    print(auto_complete_trie.search("app"))     # Output: True (We explicitly inserted "app")
    print(auto_complete_trie.search("apr"))     # Output: False (Prefix matches, but isn't a full word)

    # 2. Prefix matches (Autocomplete style)
    print(auto_complete_trie.starts_with("ap"))  # Output: True ("apple", "app", "apricot")
    print(auto_complete_trie.starts_with("ban")) # Output: True ("banana")
    print(auto_complete_trie.starts_with("cat")) # Output: False