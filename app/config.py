# app/config.py

# Enable detailed logging for development
import os

ENV = os.getenv("ENV", "prod")
DEBUG_LOG = ENV == "dev"

ACCEPTED_LANGUAGES = {"en", "fr", "it", "es"}

# SentenceTransformer model to use
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# Thresholds
REFERENCE_SIM_THRESHOLD = 0.35  # used in is_semantically_wine_related
SHORT_TERM_SIM_THRESHOLD = 0.6   # used in is_known_wine_term

# Content heuristics
MIN_TEXT_BLOCK_LENGTH = 15
MAX_SYMBOLIC_THRESHOLD = 5  # max allowed symbolic chars in a row

# Cache behavior
EMBEDDING_CACHE_SIZE = 1024

# Wine domain reference corpus (for semantic embedding)
WINE_REFERENCE_TEXT = (
    "Wine labels often list grape varieties such as Pinot Noir, Cabernet Sauvignon, Merlot, Syrah, Grenache, Tempranillo, Chardonnay, Riesling, and Chenin Blanc. "
    "Each variety brings unique characteristics — Pinot Noir is known for red fruit and earthiness, while Syrah offers spice and black fruit. "
    "Blended wines combine multiple varietals, like GSM (Grenache-Syrah-Mourvèdre) or Bordeaux-style blends with Merlot and Cabernet Franc. "
    "Regions like Bordeaux, Burgundy, Napa Valley, Barolo, Rioja, Mendoza, Mosel, Tuscany, and Swartland are world-famous for their terroirs and production styles. "
    "Subregions such as Pauillac, Rutherford, Stellenbosch, and Côte-Rôtie also influence a wine’s profile. "
    "Terms like AOC (Appellation d'Origine Contrôlée), DOCG, IGP, and AVA indicate regional quality classifications. "
    "Vintage years such as 2015, 2018, 2019, and 2020 appear on labels and signify harvest conditions. "
    "Professional tasting notes describe aromas and flavors like black cherry, cassis, green pepper, tobacco, violets, vanilla, earth, and wet stone. "
    "Descriptors like full-bodied, medium acidity, soft tannins, long finish, and complex bouquet help assess quality. "
    "Wines are often aged in French or American oak, stainless steel, or amphora, affecting flavor and texture. "
    "Winemaking techniques include wild fermentation, whole cluster pressing, lees stirring, and malolactic conversion. "
    "Labels might state 'estate grown', 'old vines', 'barrel aged', 'unfiltered', or 'hand-harvested'. "
    "Price tags often include currency values like $45, €90, USD120, or £35. "
    "ABV (Alcohol By Volume) values such as 13%, 13.5%, or 14.1% help describe wine strength. "
    "Critics like Robert Parker, Tim Atkin, Jancis Robinson, Antonio Galloni, and James Suckling publish scores. "
    "Wine Spectator, Decanter, Wine Advocate, and Vinous assign ratings like 94 points or 96/100. "
    "Food pairings include red wine with steak, white wine with seafood, or Pinot Noir with duck. "
    "Terms like terroir, minerality, acidity, body, and structure are essential for wine education."
    "Food pairings often suggest lamb with Bordeaux, duck with Pinot Noir, or cheese with Rioja. "
    "Descriptors like jammy, smoky, citrus, floral, and herbal are common in tasting notes. "
    "Textures include velvety, chalky, grippy, or lush depending on tannin and acidity. "
    "Winemaking terms like wild fermentation, lees aging, or malolactic conversion reveal style. "
    "Classification terms include Grand Cru, Premier Cru, Classico, DOCG, and IGP. "
    "Review abbreviations such as RP (Robert Parker), JS (James Suckling), and TA (Tim Atkin) may appear on wine listings. "
    "Natural, organic, and biodynamic wines are increasingly popular. "
    "Label phrases like Reserve, Crianza, and Unfiltered often signal quality and aging. "
    "Retail references may mention case discounts, magnums, or library releases. "
)

# Short wine keywords for short block rescue
SHORT_TERM_REFERENCES = [
    # Wine metadata
    "abv", "alc", "alcohol", "vintage", "score", "rating", "points", "pts",
    "price", "usd", "eur", "€", "$", "£", "retail",

    # Common descriptors
    "dry", "sweet", "bold", "tannic", "acidic", "balanced", "complex", "elegant",

    # Countries
    "france", "italy", "spain", "usa", "chile", "argentina", "germany",
    "australia", "new zealand", "portugal", "south africa", "austria",

    # Regions
    "bordeaux", "burgundy", "napa", "sonoma", "rhone", "loire", "alsace",
    "tuscany", "barolo", "mosel", "rioja", "chianti", "swartland", "mendoza",
    "willamette", "mclaren", "etna", "priorat", "rías baixas",

    # Grapes
    "pinot", "chardonnay", "syrah", "tempranillo", "grenache", "sangiovese",
    "malbec", "merlot", "cabernet", "viognier", "nebbiolo", "carignan",
    "zinfandel", "riesling", "muscat", "chenin", "barbera", "gruner", "corvina",

    # Critics
    "parker", "atkin", "suckling", "vinous", "decanter", "jancis", "cellartracker",

    # Vintages
    "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025",

    # Pairing keywords
    "steak", "duck", "seafood", "cheese", "pasta", "lamb", "salmon", "roast", "charcuterie",

    # Tasting descriptors
    "floral", "spicy", "earthy", "citrus", "herbal", "vanilla", "blackberry", "cherry",
    "stone fruit", "minerality", "chalky", "smoky", "nutty", "jammy",

    # Texture & structure
    "grippy", "silky", "velvety", "chalky", "lush", "round", "structured", "linear",

    # Label terms & classifications
    "reserve", "reserva", "grand cru", "crianza", "superiore", "premier cru", "village", 
    "classico", "IGP", "DOC", "DOCG", "AVA", "AOC",

    # Critic initials / abbreviations
    "rp", "js", "jr", "ta", "wa", "ws", "we", "vn",

    # Production techniques
    "unfiltered", "natural", "organic", "biodynamic", "oak aged", "barrel fermented",
    "wild yeast", "lees", "malolactic", "hand-harvested",
]
