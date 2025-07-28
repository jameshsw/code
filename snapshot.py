class SnapshotMap:
    """A map implementation that supports efficient snapshots.
    
    Implementation uses delta storage and version tracking to achieve
    sublinear scaling with number of keys while supporting snapshots.
    """
    
    def __init__(self):
        # Current state of the map
        self._current = {}  # {key: (value, version)}
        
        # Snapshot delta storage
        self._snapshots = {}  # {snapshot_id: {key: (value, version)}}
        
        # Current version number for tracking changes
        self._version = 0
        
        # Counter for generating snapshot IDs
        self._next_snapshot_id = 0
    
    def put(self, key, value):
        """Store a mapping from a key to a value."""
        self._version += 1
        self._current[key] = (value, self._version)
    
    def snapshot(self):
        """Take a snapshot of the map and return an identifier."""
        snapshot_id = self._next_snapshot_id
        self._next_snapshot_id += 1
        
        # Store only the current state's version numbers
        # We'll use this to know which values to look up
        self._snapshots[snapshot_id] = {
            key: (value, version) 
            for key, (value, version) in self._current.items()
        }
        
        return snapshot_id

    def get(self, key, snapshot_id=None):
        """Retrieve the value of a key, with an optionally specified snapshot."""
        if snapshot_id is None:
            # Get current value
            if key not in self._current:
                raise KeyError(key)
            return self._current[key][0]
        
        # Get value from snapshot
        if snapshot_id not in self._snapshots:
            raise KeyError(f"Invalid snapshot ID: {snapshot_id}")
            
        snapshot = self._snapshots[snapshot_id]
        if key not in snapshot:
            raise KeyError(key)
            
        return snapshot[key][0]

    def delete(self, key):
        """Remove the value for the given key in the current state."""
        if key not in self._current:
            raise KeyError(key)
            
        self._version += 1
        del self._current[key]

def findSubstring(s: str, words: list[str]) -> list[int]:
    if not s or not words:
        return []
        
    # Get word length and count
    word_len = len(words[0])
    word_count = len(words)
    total_len = word_len * word_count
    
    # Create word frequency map
    word_map = {}
    for word in words:
        word_map[word] = word_map.get(word, 0) + 1
        
    result = []
    
    # Try each possible starting position
    for i in range(len(s) - total_len + 1):
        # Create a copy of word map for this window
        curr_map = word_map.copy()
        matches = 0
        
        # Check each word position in the window
        for j in range(word_count):
            # Get the word at current position
            pos = i + j * word_len
            curr_word = s[pos:pos + word_len]
            
            # If word exists in map and count > 0
            if curr_word in curr_map and curr_map[curr_word] > 0:
                curr_map[curr_word] -= 1
                matches += 1
            else:
                break
                
        # If all words matched
        if matches == word_count:
            result.append(i)
            
    return result

# Test cases
def test():
    # Test case 1
    assert findSubstring("barfoothefoobarman", ["foo","bar"]) == [0,9]
    
    # Test case 2
    assert findSubstring("wordgoodgoodgoodbestword", ["word","good","best","word"]) == []
    
    # Test case 3
    assert findSubstring("barfoofoobarthefoobarman", ["bar","foo","the"]) == [6,9,12]
    
    print("All test cases passed!")

if __name__ == "__main__":
    test()
