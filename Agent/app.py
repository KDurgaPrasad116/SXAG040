from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from services.input_processor import extract_text
from services.clause_splitter import split_clauses
from services.llm_classifier import classify_clause

app = FastAPI()

# 🔹 Enable CORS (for frontend later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "Legal Clause Analyzer API Running 🚀"}


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        # 🔹 Step 1: Extract text
        text = extract_text(file)

        # 🔹 Step 2: Split into clauses
        clauses = split_clauses(text)

        results = []
        positive_clauses = []
        negative_clauses = []

        # 🔹 Step 3: Classify each clause
        for clause in clauses:
            result = classify_clause(clause)

            results.append(result)

            # 🔹 Step 4: Categorization
            if result["type"] == "Positive":
                positive_clauses.append(result)

            elif result["type"] == "Negative":
                negative_clauses.append(result)

        # 🔹 Step 5: Sort positives by benefit score
        positive_clauses = sorted(
            positive_clauses,
            key=lambda x: x["benefit_score"],
            reverse=True
        )

        return {
            "total_clauses": len(clauses),
            "all_results": results,
            "positive_clauses": positive_clauses,
            "negative_clauses": negative_clauses
        }

    except Exception as e:
        return {"error": str(e)}