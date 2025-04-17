from app.services.llm.llm_search import generate_wine_analysis_from_llm
from app.services.llm.search_and_summarize import summarize_wine_info

def test_summarize_wine_info():
    wine_name = "Opus One 2015"
    result = summarize_wine_info(wine_name)

    print("\n--- Gemini Web Summary ---")
    for key, value in result.items():
        print(f"{key}: {value}")
        