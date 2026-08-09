import sys
from pathlib import Path
from src.routing.query_classifier import QueryClassifier, QueryType
from src.prompts.prompt_factory import PromptFactory
from src.models.search_result import SearchResponse, SearchResult
from src.evaluation.confidence import ConfidenceScorer
from src.recommendation.question_generator import QuestionGenerator
from src.search.hybrid_search import HybridSearch

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_query_classifier():
    assert QueryClassifier.classify("explain deadlock") == QueryType.EXPLANATION
    assert QueryClassifier.classify("generate 20 questions") == QueryType.MCQ_GENERATION
    assert QueryClassifier.classify("summarize this document") == QueryType.SUMMARY
    assert QueryClassifier.classify("find the document about ML") == QueryType.DOCUMENT_SEARCH
    assert QueryClassifier.classify("hello") == QueryType.GENERAL_CHAT
    assert QueryClassifier.classify("what is the capital of France?") == QueryType.FACTUAL
    print("Query Classifier tests passed.")

def test_prompt_factory():
    prompt = PromptFactory.get_prompt(QueryType.EXPLANATION, "explain X", "context", "")
    assert "step-by-step" in prompt.lower() or "explain" in prompt.lower()
    print("Prompt Factory tests passed.")

def test_confidence_scorer():
    resp = SearchResponse(
        query="test",
        results=[SearchResult("1", "doc", "chunk", "text", 1, 0.8, {})],
        total_results=1,
        search_time_seconds=0.1,
        embedding_time_seconds=0.1,
        retrieval_time_seconds=0.1
    )
    conf = ConfidenceScorer.compute_confidence(resp)
    assert conf == "HIGH"
    print("Confidence Scorer tests passed.")

def test_question_generator():
    ans = "A deadlock occurs when..."
    qs = QuestionGenerator.generate_questions(ans, [])
    assert len(qs) == 3
    assert "deadlock" in qs[0].lower() or "coffman" in qs[1].lower()
    print("Question Generator tests passed.")

def test_hybrid_search():
    hs = HybridSearch()
    dense_results = [
        ({"chunk_text": "apple banana"}, 0.9),
        ({"chunk_text": "orange banana"}, 0.8)
    ]
    fused = hs.fuse("apple", dense_results)
    assert len(fused) == 2
    # apple banana should be ranked higher because of dense score + bm25
    assert fused[0][0]["chunk_text"] == "apple banana"
    print("Hybrid Search tests passed.")

if __name__ == "__main__":
    print("=================================")
    print("KNOWSPHERE PHASE 6A TESTS")
    print("=================================")
    test_query_classifier()
    test_prompt_factory()
    test_confidence_scorer()
    test_question_generator()
    test_hybrid_search()
    print("ALL TESTS PASSED.")
