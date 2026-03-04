# config.py — single source of truth for all settings

LM_STUDIO_URL   = "http://192.168.0.107:1234/v1"
REASONING_MODEL = "qwen2.5-coder-7b-instruct"
EMBEDDING_MODEL = "text-embedding-all-minilm-l6-v2-embedding"
CHROMA_DIR      = "./chroma_store"
MAX_TOKENS      = 1024
TEMP_CODE       = 0.1   # Low = deterministic code
TEMP_EXPLAIN    = 0.3   # Slightly higher for explanations

# Aliases for any code using the newer names
CHROMA_PERSIST_DIR = CHROMA_DIR
TEMPERATURE_CODE   = TEMP_CODE
TEMPERATURE_CHAT   = TEMP_EXPLAIN

AUTO_QUESTIONS = [
    "What are the overall statistics of this dataset?",
    "Which columns have the most missing values?",
    "What is the distribution of the most important column?",
    "What are the top correlations between numeric columns?",
    "What is the most interesting pattern in this data?",
]