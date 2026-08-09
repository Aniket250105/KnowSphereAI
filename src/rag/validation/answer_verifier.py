from src.rag.interfaces.base_answer_verifier import BaseAnswerVerifier
from src.models.rag_response import RAGResponse
from src.models.evaluation_result import VerificationResult

class AnswerVerifier(BaseAnswerVerifier):
    def verify(self, response: RAGResponse) -> VerificationResult:
        reasons = []
        passed = True
        
        answer = response.answer.strip()
        
        # 1. Empty Answer
        if not answer:
            reasons.append("Answer is empty.")
            passed = False
            return VerificationResult(passed, reasons)
            
        # 2. Too Short
        if len(answer) < 10:
            reasons.append("Answer is excessively short.")
            passed = False
            
        # 3. "I don't know" despite good retrieval
        negative_phrases = ["i don't know", "i cannot find", "i couldn't find", "i am sorry"]
        is_negative = any(phrase in answer.lower() for phrase in negative_phrases)
        
        # If confidence is HIGH but we said we don't know, it's a conflict
        if is_negative and response.confidence == "HIGH":
            reasons.append("Answer indicates ignorance despite HIGH retrieval confidence.")
            passed = False
            
        # 4. Missing Citations (if sources exist and it's not a negative phrase)
        if response.sources and not is_negative:
            if "[" not in answer or "]" not in answer:
                reasons.append("Good sources retrieved but no citations used in the answer.")
                # We don't fail verification entirely for this, just a warning, but we record the reason.
                
        return VerificationResult(passed, reasons)
