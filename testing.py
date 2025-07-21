#This library provides a function to count the number of occurrences of each character in a string.
from collections import Counter

s = 'ama'

def is_palindrome(s):
    # Count the occurrences of each character in the string
    char_count = Counter(s)
    
    # Count how many characters have an odd count
    odd_count = sum(1 for count in char_count.values() if count % 2 != 0)
    
    # A string can be rearranged to form a palindrome if at most one character has an odd count
    return odd_count <= 1

print(is_palindrome(s))  # Output: True, since "ama" can be rearranged to "ama" or "aam" which is a palindrome