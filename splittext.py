def split(s, vocab):
    # Base case 1: if the whole string is empty, return empty list
    if s == "":
        return []

    # Initialize the best result as None (to keep track of the minimal split)
    best = None

    # Try every possible prefix from s
    for i in range(1, len(s) + 1):
        prefix = s[:i]

        # Check if prefix is in vocabulary
        if prefix in vocab:
            # Recursively split the rest of the string
            rest = split(s[i:], vocab)

            # If rest is not None (valid split), try to update best result
            if rest is not None:
                candidate = [prefix] + rest
                # Update best if it's the first found or shorter than current best
                if best is None or len(candidate) < len(best):
                    best = candidate

    # Return the best valid split (or None if not found)
    return best
