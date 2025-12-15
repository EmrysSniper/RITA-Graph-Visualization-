"""
aviation_semantic_pipeline_md.py
────────────────────────────────
Full end‑to‑end pipeline that

1. Cleans and tokenises aviation accident narratives while preserving
   hyphenated aircraft models (e.g. "Boeing-747") and other critical terms.
2. Builds dynamic low‑ and high‑frequency stop‑lists to filter noise or
   over‑represented generic words.
3. Runs spaCy (with the **en_core_web_md** model) to extract aircraft,
   damage descriptions, causes, and locations using NER + pattern rules.
4. Outputs the enriched results as a full JSON file.
"""

import json, re, itertools, collections, pathlib
import pandas as pd

# ── CONFIG ─────────────────────────────────────────────
FILE_PATH = r"C:\\Users\\olaye\\Documents\\UARC\\final_extracted_data.json"
OUTPUT_JSON = r"C:\\Users\\olaye\\Documents\\UARC\\semantic_enriched_output.json"
LOW_FREQ_THRESHOLD = 2
HIGH_FREQ_DOC_RATIO = 0.90

# ── CLEANING ───────────────────────────────────────────
MODEL_PAT   = r'\b[A-Z][a-zA-Z]+-\d+\b'
COMPOUND_PAT = r'\b\w+-\w+\b'
PRESERVE_RE  = re.compile(f'(?:{MODEL_PAT}|{COMPOUND_PAT})')

def clean_text(text: str) -> str:
    protected = {}
    def _mask(match):
        key = f"__TOK{len(protected)}__"
        protected[key] = match.group(0)
        return key
    text_masked = PRESERVE_RE.sub(_mask, text)
    text_clean = re.sub(r'[^\w\s-]', ' ', text_masked).lower()
    for key, original in protected.items():
        text_clean = text_clean.replace(key.lower(), original.lower())
    return re.sub(r'\s+', ' ', text_clean).strip()

# ── FREQUENCY FILTER ───────────────────────────────────
def build_frequency_filters(docs, low_th=LOW_FREQ_THRESHOLD, high_ratio=HIGH_FREQ_DOC_RATIO):
    from nltk.corpus import stopwords
    import nltk; nltk.download('stopwords', quiet=True)
    stop_words = set(stopwords.words('english'))
    all_tokens = list(itertools.chain.from_iterable(doc.split() for doc in docs))
    freq = collections.Counter(all_tokens)
    low_freq  = {tok for tok, c in freq.items() if c < low_th}
    high_freq = {tok for tok, c in freq.items() if c > high_ratio * len(docs)}
    return stop_words | low_freq | high_freq

# ── SPACY EXTRACTION ───────────────────────────────────
import spacy

try:
    nlp = spacy.load("en_core_web_md")
except OSError:
    print("[INFO] en_core_web_md not found. Downloading...")
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_md"], check=True)
    nlp = spacy.load("en_core_web_md")

def extract_entities(text):
    doc = nlp(text)
    ents = collections.defaultdict(list)
    for ent in doc.ents:
        if ent.label_ in ("ORG", "GPE", "DATE", "PRODUCT"):
            ents[ent.label_].append(ent.text)
    for sent in doc.sents:
        s = sent.text.strip()
        low = s.lower()
        if re.search(r'\b(boeing|cessna|piper|airbus|beech|lancair|ryan|douglas)\b', low):
            ents["aircraft"].append(s)
        if "damage" in low or "substantial" in low:
            ents["damage"].append(s)
        if re.search(r'\b(failure|stall|loss of engine|loss of control|fatigue)\b', low):
            ents["cause"].append(s)
    return {k: list(dict.fromkeys(v)) for k, v in ents.items()}

# ── MAIN PIPELINE ──────────────────────────────────────
def main():
    with open(FILE_PATH, encoding="utf-8") as f:
        raw = json.load(f)

    filtered_items = [item for item in raw if item.get("Analysis") not in (None, "Not found")]
    analyses = [item["Analysis"] for item in filtered_items]
    cleaned = [clean_text(a) for a in analyses]
    filter_set = build_frequency_filters(cleaned)

    keywords_per_doc = [
        [t for t in doc.split() if t not in filter_set] for doc in cleaned
    ]
    entities = [extract_entities(a) for a in analyses]

    output = []
    for item, ent, kw in zip(filtered_items, entities, keywords_per_doc):
        aircraft_text = item.get("Flight Information", {}).get("Aircraft", "")
        entry = {
            "file_name"    : item["File Name"],
            "aircraft"     : list(set(ent.get("aircraft", []) + [aircraft_text] if aircraft_text else ent.get("aircraft", []))),
            "damage_notes" : ent.get("damage", []),
            "cause_notes"  : ent.get("cause", []),
            "keywords"     : kw
        }
        output.append(entry)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"[✔] Output written to {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
