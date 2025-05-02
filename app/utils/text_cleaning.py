import logging
import re
import string
from functools import lru_cache
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
from sentence_transformers import SentenceTransformer, util
from app.config import (
    DEBUG_LOG,
    ACCEPTED_LANGUAGES,
    EMBEDDING_MODEL_NAME,
    WINE_REFERENCE_TEXT,
    SHORT_TERM_REFERENCES,
    REFERENCE_SIM_THRESHOLD,
    SHORT_TERM_SIM_THRESHOLD,
    MIN_TEXT_BLOCK_LENGTH,
    MAX_SYMBOLIC_THRESHOLD,
    EMBEDDING_CACHE_SIZE,
)
'''
# Uncomment for running local test file to debug
if DEBUG_LOG:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
'''

logger = logging.getLogger(__name__)
DetectorFactory.seed = 42

embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
reference_embedding = embedding_model.encode(WINE_REFERENCE_TEXT, convert_to_tensor=True)
short_term_embeddings = embedding_model.encode(SHORT_TERM_REFERENCES, convert_to_tensor=True)

@lru_cache(maxsize=EMBEDDING_CACHE_SIZE)
def is_accepted_language(text: str) -> bool:
    try:
        return detect(text) in ACCEPTED_LANGUAGES
    except LangDetectException:
        return False

def is_probably_binary(text: str, threshold: float = 0.3) -> bool:
    if not text or len(text) < 100:
        return True
    printable_ratio = sum(c in string.printable for c in text) / len(text)
    return printable_ratio < (1 - threshold)

def is_semantically_wine_related(text: str, threshold: float = REFERENCE_SIM_THRESHOLD) -> bool:
    if len(text.strip()) < MIN_TEXT_BLOCK_LENGTH:
        return False
    try:
        vec = embedding_model.encode(text, convert_to_tensor=True)
        score = util.cos_sim(vec, reference_embedding).item()
        if DEBUG_LOG:
            logger.info(f"Semantic wine score: {score:.3f} — {text[:60]}")
        return score >= threshold
    except Exception as e:
        logger.warning(f"[Embed Check Error] {e}")
        return False

def is_known_wine_term(text: str, threshold: float = SHORT_TERM_SIM_THRESHOLD) -> bool:
    text = text.lower().strip()
    if len(text) > 30:
        return False
    try:
        vec = embedding_model.encode(text, convert_to_tensor=True)
        score = util.cos_sim(vec, short_term_embeddings).max().item()
        return score >= threshold
    except Exception as e:
        logger.warning(f"[Embed ShortTerm Error] {e}")
        return False

def contains_price_info(text: str) -> bool:
    return bool(re.search(r"(usd|€|\$|£|eur)\s?\d{1,4}", text.lower()))

def clean_non_human_text(text: str) -> str:
    if is_probably_binary(text):
        return ""
    text = re.sub(r"[\x00-\x1F\x7F-\x9F]", "", text)

    while True:
        old = text
        text = re.sub(r"[ \t\r\f\v]+", " ", text)
        text = re.sub(r"[ \t]+(?=\n)", "", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        if old == text:
            break

    text = re.sub(r"\s*\n\s*", "\n", text)
    text = re.sub(r"(\n\s*){2,}", "\n\n", text)

    lines = text.splitlines()
    return "\n".join(
        line.strip()
        for line in lines
        if not re.fullmatch(rf"[\W_]{{{MAX_SYMBOLIC_THRESHOLD},}}", line.strip())
    ).strip()

def clean_text_blocks(text: str) -> str:
    blocks = re.split(r"\n{2,}", text)
    cleaned = []
    reasons = {"short": 0, "symbolic": 0, "non_accepted_lang": 0, "kept": 0}

    for block in blocks:
        block = re.sub(r"[^\x20-\x7E\n\r\t]", "", block).strip()
        if not block:
            continue

        if len(block) < MIN_TEXT_BLOCK_LENGTH:
            if not (is_known_wine_term(block) or is_semantically_wine_related(block) or contains_price_info(block)):
                if DEBUG_LOG:
                    logger.info(f"SKIP: Too short: '{block}'")
                reasons["short"] += 1
                continue

        if re.search(rf"[{{}}|\\@#$%^&*_=~`<>]{{{MAX_SYMBOLIC_THRESHOLD},}}", block):
            reasons["symbolic"] += 1
            continue

        if len(block) > 50 and not is_accepted_language(block):
            if not is_semantically_wine_related(block):
                if DEBUG_LOG:
                    logger.info(f"SKIP: Not accepted language: '{block[:60]}...'")
                reasons["non_accepted_lang"] += 1
                continue

        cleaned.append(block)
        reasons["kept"] += 1

    if DEBUG_LOG:
        logger.info(f"Block filtering reasons: {reasons}")
    return "\n\n".join(cleaned).strip()

def clean_aggressively(raw_text: str) -> str:
    return clean_text_blocks(clean_non_human_text(raw_text))