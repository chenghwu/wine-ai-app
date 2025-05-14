def clean_aroma_clusters(aroma: dict) -> dict:
    """
    Remove aroma clusters that have empty descriptor lists.
    """
    return {
        cluster: descriptors
        for cluster, descriptors in aroma.items()
        if descriptors  # exclude empty lists
    }