from app.services.scrapers.vivino import scrape_vivino
from app.services.scrapers.decanter import scrape_decanter
from app.services.scrapers.wine_enthusiast import scrape_wine_enthusiast
from app.services.scrapers.wine_searcher import scrape_wine_searcher
from app.services.scrapers.wine_spectator import scrape_wine_spectator
from app.services.scrapers.web_search import scrape_top_results

from app.services.llm_summarizer import summarize_sources_with_gemini

# Step 1: Run all scraper functions
def collect_all_sources(wine_name: str) -> list:
    return [
        scrape_vivino(wine_name),
        scrape_decanter(wine_name),
        scrape_wine_enthusiast(wine_name),
        scrape_wine_searcher(wine_name),
        scrape_wine_spectator(wine_name),
        scrape_top_results(wine_name)
    ]

# Step 2: Summarize via Gemini LLM
def enrich_wine_analysis_from_sources(wine_name: str) -> dict:
    sources = collect_all_sources(wine_name)

    # Step 3: Ask Gemini to summarize + generate SAT-style output
    summary = summarize_sources_with_gemini(wine_name, sources)

    # Return both raw source data + Gemini summary
    return {
        "wine_name": wine_name,
        "sources": sources,
        "summary": summary
    }