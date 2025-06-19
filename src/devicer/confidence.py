from .hashing import get_tlsh_hash, get_hash_difference
import math

def compare_lists(data1: list, data2: list) -> tuple[int, int]:
    """
    Compare two lists and return the count of matching elements and total elements.
    
    Args:
        data1 (list): First list containing data.
        data2 (list): Second list containing data.
    
    Returns:
        tuple: A tuple containing the count of matching elements and total elements compared.
    """
    fields = 0
    matches = 0
    max_length = max(len(data1), len(data2))
    for i in range(max_length):
        if data1[i] and data2[i]:
            fields += 1
            if isinstance(data1[i], dict) and isinstance(data2[i], dict):
                sub_matches, sub_fields = compare_dictionaries(data1[i], data2[i])
                matches += sub_matches
                fields += sub_fields - 1
            elif isinstance(data1[i], list) and isinstance(data2[i], list):
                sub_matches, sub_fields = compare_lists(data1[i], data2[i])
                matches += sub_matches
                fields += sub_fields - 1
            if data1[i] == data2[i]:
                matches += 1
    return matches, fields

def compare_dictionaries(data1: dict, data2: dict) -> tuple[int, int]:
    """
    Compare two dictionaries and return the count of matching fields and total fields.
    
    Args:
        data1 (dict): First dictionary containing data.
        data2 (dict): Second dictionary containing data.
    
    Returns:
        tuple: A tuple containing the count of matching fields and total fields compared.
    """
    fields = 0
    matches = 0
    for key in data1:
        if key in data2:
            fields += 1
            if isinstance(data1[key], dict) and isinstance(data2[key], dict):
                sub_matches, sub_fields = compare_dictionaries(data1[key], data2[key])
                matches += sub_matches
                fields += sub_fields - 1 # Subtract 1 to avoid double counting the key
            elif isinstance(data1[key], list) and isinstance(data2[key], list):
                sub_matches, sub_fields = compare_lists(data1[key], data2[key])
                matches += sub_matches
                fields += sub_fields - 1
            if data1[key] == data2[key]:
                matches += 1
    return matches, fields

def calculate_confidence(data1: dict, data2: dict) -> float:
    """
    Calculate the confidence score based on two dictionaries of data.
    
    Args:
        data1 (dict): First dictionary containing data.
        data2 (dict): Second dictionary containing data.
    
    Returns:
        float: Confidence score calculated as the ratio of the sum of values in data1 to the sum of values in data2.
    """
    matches, fields = compare_dictionaries(data1, data2)
    
    if fields == 0 or matches == 0:
        return 0

    hash1 = get_tlsh_hash(str(data1).encode('utf-8'))
    hash2 = get_tlsh_hash(str(data2).encode('utf-8'))
    difference_score = get_hash_difference(hash1, hash2)

    inverse_match_score = 1 - (matches / fields)
    x = 1.3 * difference_score * inverse_match_score
    if (inverse_match_score == 0 or difference_score == 0):
        return 100
    confidence_score = 100 / (1 + math.e ** (-4.5 + (0.3 * x)))
    return confidence_score