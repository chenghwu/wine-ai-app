from app.config import EMBEDDING_MODEL_NAME
from app.constants.food_base_categories import FOOD_BASE_CATEGORIES
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer(EMBEDDING_MODEL_NAME)

# Pre-compute base category embedding centroids
CATEGORY_EMBEDDINGS = {
    cat: model.encode(examples, normalize_embeddings=True)
    for cat, examples in FOOD_BASE_CATEGORIES.items() if examples
}

def find_base_category(food_item: str, threshold: float = 0.45) -> str:
    item_emb = model.encode(f"A dish of {food_item}", normalize_embeddings=True)
    best_category, best_score = "Other", -1.0

    for cat, example_embeds in CATEGORY_EMBEDDINGS.items():
        score = max(np.dot(item_emb, e) for e in example_embeds)
        print(f"{food_item} → {cat}: {score:.3f}")
        if score > best_score:
            best_category, best_score = cat, score

    return best_category if best_score > threshold else "Other"