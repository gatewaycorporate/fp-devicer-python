import tlsh;

def get_tlsh_hash(data: bytes) -> str:
    """
    Generate a TLSH hash for the given data.

    Args:
        data (bytes): The input data to hash.

    Returns:
        str: The TLSH hash as a hexadecimal string.
    """
    tlsh_hash = tlsh.hash(data)
    return tlsh_hash

def get_hash_difference(hash1: str, hash2: str) -> int:
    """
    Calculate the difference between two TLSH hashes.

    Args:
        hash1 (str): The first TLSH hash.
        hash2 (str): The second TLSH hash.

    Returns:
        int: The difference score between the two hashes.
    """
    return tlsh.diff(hash1, hash2)