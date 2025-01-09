## Function for help
# Put a bit on index -> void
def set_bit(progress, index):
    byte_index = index // 8
    bit_index  = index % 8
    progress[byte_index] |= (1 << bit_index)

# Check bit on index -> bool
def is_bit_set(progress, index):
    byte_index = index // 8
    bit_index  = index % 8
    return (progress[byte_index] & (1 << bit_index)) != 0

# Get first 5 not learned verb index -> int
def find_next_unlearned(progress, size):
    indexes = []
    for i in range(0, len(progress) * 8):
        if not is_bit_set(progress, i):
            indexes.append(i + 1)
            if len(indexes) == size:
                break
    return indexes
#
## END HELP FUNCTION