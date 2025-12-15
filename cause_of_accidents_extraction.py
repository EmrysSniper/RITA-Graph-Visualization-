import json
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter

# Load the JSON data
file_path = "C:\\Users\\olaye\\Documents\\final_extracted_data.json"  # Update as needed
with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Extract file names and causes
file_names = []
causes = []

for record in data:
    cause = record.get("Probable Cause and Findings", "").strip()
    if cause and cause.lower() != "not found":
        causes.append(cause)
        file_names.append(record.get("File Name", "Unknown File"))

# Vectorize the causes
vectorizer = TfidfVectorizer(stop_words="english")
tfidf_matrix = vectorizer.fit_transform(causes)
similarity_matrix = cosine_similarity(tfidf_matrix)

# Group similar causes
threshold = 0.65
groups = []
visited = set()

for i in range(len(causes)):
    if i in visited:
        continue
    group = [(file_names[i], causes[i])]
    visited.add(i)
    for j in range(i + 1, len(causes)):
        if j not in visited and similarity_matrix[i][j] >= threshold:
            group.append((file_names[j], causes[j]))
            visited.add(j)
    if len(group) > 1:
        groups.append(group)

# Helper: Clean and tokenize for summary
def extract_keywords(texts, top_n=5):
    words = re.findall(r'\b[a-zA-Z]+\b', " ".join(texts).lower())
    common = Counter(words).most_common(top_n)
    return [word for word, count in common]

# Save to output file
output_file = "C:\\Users\\olaye\\Documents\\grouped_causes_summary.txt"
with open(output_file, "w", encoding="utf-8") as f:
    for idx, group in enumerate(groups, 1):
        f.write(f"Group {idx} (Similar Causes of Accidents):\n")
        causes_only = []
        for fname, cause in group:
            causes_only.append(cause)
            f.write(f"\nFile: {fname}\nCause:\n{cause}\n")
        # Extract keywords
        keywords = extract_keywords(causes_only)
        f.write(f"\n📝 Summary Keywords: {', '.join(keywords)}\n")
        f.write("\n" + "="*90 + "\n\n")

print(f"Grouped causes with summaries saved to: {output_file}")
