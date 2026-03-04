import re
import pandas as pd
from llm_client import generate_code, generate_explanation
from rag_engine import retrieve_context
from visualizer import auto_chart
from config     import AUTO_QUESTIONS


def _extract_code(raw: str) -> str:
    raw = re.sub(r"```python", "", raw)
    raw = re.sub(r"```",       "", raw)
    lines = [l for l in raw.strip().splitlines() if l.strip()]
    return "\n".join(lines).strip()


# Safe subset of builtins — enough for pandas code, no file/network access
_SAFE_BUILTINS = {
    "len": len, "str": str, "int": int, "float": float, "bool": bool,
    "list": list, "dict": dict, "tuple": tuple, "set": set,
    "range": range, "enumerate": enumerate, "zip": zip, "map": map,
    "filter": filter, "sorted": sorted, "reversed": reversed,
    "min": min, "max": max, "sum": sum, "abs": abs, "round": round,
    "any": any, "all": all, "isinstance": isinstance, "type": type,
    "print": print, "repr": repr, "hasattr": hasattr, "getattr": getattr,
    "ValueError": ValueError, "TypeError": TypeError, "KeyError": KeyError,
    "True": True, "False": False, "None": None,
}


def _safe_exec(code: str, df: pd.DataFrame):
    import numpy as np
    local = {"df": df, "pd": pd, "np": np}
    try:
        exec(code, {"__builtins__": _SAFE_BUILTINS}, local)
        if "result" in local:
            return local["result"], None
        user_vars = [k for k in local if k not in ("df", "pd", "np")]
        if user_vars:
            return local[user_vars[-1]], None
        return None, "No result variable found"
    except Exception as e:
        return None, str(e)


def answer_question(df: pd.DataFrame,
                    question: str,
                    history: list) -> dict:

    context = retrieve_context(question)

    prompt = f"""
Dataset context — use these EXACT column names:
{context}

DataFrame is loaded as variable df.
Question: "{question}"

Rules:
- Store answer in variable named result
- Only use pandas (df and pd available)
- No imports
- Max 6 lines
- Return ONLY code
"""
    raw  = generate_code(
        system="Return only Python pandas code. No markdown.",
        user=prompt
    )
    code = _extract_code(raw)

    result, error = _safe_exec(code, df)

    if error:
        retry = f"""
{prompt}
Previous attempt failed: {error}
Column names are case-sensitive. Use exact names from context.
Write simpler corrected code.
"""
        raw           = generate_code(
            system="Return only Python code. Fix the error.",
            user=retry
        )
        code          = _extract_code(raw)
        result, error = _safe_exec(code, df)

    if error or result is None:
        return {
            "answer"      : "I wasn't able to compute an answer for that question. Could you try rephrasing it?",
            "raw_result"  : None,
            "code"        : code,
            "explanation" : f"Error: {error}",
            "chart"       : None
        }

    explain = generate_explanation(
        system="You are a data analyst explaining results to a business manager. Be concise, use plain English, and include specific numbers from the result.",
        user=f"""
Question: "{question}"
Pandas code that ran: {code}
Raw result: {str(result)[:500]}

Write 2-3 sentences explaining this finding in natural language.
Include actual numbers and percentages from the result.
Do NOT mention code\
    , pandas, or DataFrames — speak as if you analyzed it yourself.
"""
    )

    return {
        "answer"      : explain,
        "raw_result"  : str(result)[:300],
        "code"        : code,
        "explanation" : explain,
        "chart"       : auto_chart(question, result, df)
    }


def run_auto_insights(df: pd.DataFrame) -> list:
    ICONS    = ["📊", "⚠️", "📈", "🔗", "💡"]
    insights = []
    for i, q in enumerate(AUTO_QUESTIONS):
        try:
            out = answer_question(df, q, [])
            insights.append({
                "icon"       : ICONS[i],
                "question"   : q,
                "answer"     : str(out["answer"])[:120],
                "explanation": str(out["explanation"])[:160],
                "code"       : out.get("code", ""),
                "chart"      : out.get("chart"),
            })
        except Exception as e:
            insights.append({
                "icon"       : ICONS[i],
                "question"   : q,
                "answer"     : "Could not compute",
                "explanation": str(e)[:100],
                "code"       : "",
                "chart"      : None,
            })
    return insights