from sentence_transformers import SentenceTransformer, util
from app.config import EMBEDDING_MODEL_NAME, LONG_FINISH_PHRASES, LONG_FINISH_SIM_THRESHOLD
from app.utils.aroma_lexicon import aroma_lexicon
from app.utils.post_llm_process import clean_aroma_clusters
import logging
import re

logger = logging.getLogger(__name__)
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

def analyze_wine_profile(profile: dict) -> dict:
    appearance = profile.get("appearance", "").lower()
    nose = profile.get("nose", "").lower()
    palate = profile.get("palate", "").lower()
    aroma = clean_aroma_clusters(profile.get("aroma", {}) or {})

    score = 0
    criteria = []

    # === B: Balance ===
    if "balanced" in palate or "balance" in palate:
        score += 1
        criteria.append("Balance")

    # === L: Length ===
    long_finish_vecs = embedding_model.encode(LONG_FINISH_PHRASES, convert_to_tensor=True)

    def is_semantically_long_finish(palate_text: str) -> bool:
        try:
            # Extract possible finish-related phrases (simple heuristic)
            finish_phrases = [
                p.strip()
                for p in re.split(r"[,.]", palate_text)
                if "finish" in p.lower()
            ]
            if not finish_phrases:
                return False

            for phrase in finish_phrases:
                vec = embedding_model.encode(phrase, convert_to_tensor=True)
                sim = util.cos_sim(vec, long_finish_vecs).max().item()
                if sim >= LONG_FINISH_SIM_THRESHOLD:
                    return True
            return False
        except Exception as e:
            logger.warning(f"[Semantic Finish Check Failed] {e}")
            return False

    if any(phrase in palate for phrase in LONG_FINISH_PHRASES):
        score += 1
        criteria.append("Length")
    else:
        if is_semantically_long_finish(palate):
            score += 1
            criteria.append("Length")

    # === I: Intensity (both must be pronounced) ===
    if "pronounced" in nose and "pronounced" in palate:
        score += 1
        criteria.append("Intensity")

    # === C: Complexity ===
    cluster_count = len(aroma)
    descriptor_count = sum(len(v) for v in aroma.values())

    if (cluster_count >= 3 and descriptor_count >= 6) or (cluster_count >= 4):
        score += 1
        criteria.append("Complexity")

    quality_map = {
        4: "Outstanding",
        3: "Very Good",
        2: "Good",
        1: "Acceptable",
        0: "Poor"
    }

    clusters = sorted(aroma.keys())
    descriptors = sorted({desc for v in aroma.values() for desc in v})

    return {
        "criteria": criteria,
        "score": score,
        "quality": quality_map.get(score, "Unknown"),
        "aroma": aroma,
        "clusters": clusters,
        "descriptors": descriptors
    }