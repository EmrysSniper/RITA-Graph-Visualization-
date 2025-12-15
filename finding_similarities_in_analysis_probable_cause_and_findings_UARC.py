import json
import os
from collections import defaultdict
from difflib import SequenceMatcher
from concurrent.futures import ThreadPoolExecutor


def clean_text(text):

    return ' '.join(text.splitlines())


def calculate_similarity(text1, text2):

    return SequenceMatcher(None, text1, text2).ratio()


def compare_entries(i, analyses, probable_causes):

    similarities = []

    for j in range(i + 1, len(analyses)):

        analysis_similarity = calculate_similarity(analyses[i], analyses[j])

        cause_similarity = calculate_similarity(probable_causes[i], probable_causes[j])

        similarities.append({

            'Entry1': i,

            'Entry2': j,

            'Analysis_Similarity': analysis_similarity,

            'Probable_Cause_Similarity': cause_similarity

        })

    return similarities


def find_similarities(json_path, output_txt_path):

    with open(json_path, 'r', encoding='utf-8') as file:

        data = json.load(file)


    analyses = [clean_text(entry["Analysis"]) for entry in data]

    probable_causes = [clean_text(entry["Probable Cause and Findings"]) for entry in data]


    similarities = []

    with ThreadPoolExecutor() as executor:

        futures = [executor.submit(compare_entries, i, analyses, probable_causes) for i in range(len(analyses))]

        for future in futures:

            similarities.extend(future.result())


    with open(output_txt_path, 'w', encoding='utf-8') as output_file:

        for similarity in similarities:

            output_file.write(f"Entry1: {similarity['Entry1']}, Entry2: {similarity['Entry2']}\n")

            output_file.write(f"Analysis Similarity: {similarity['Analysis_Similarity']}\n")

            output_file.write(f"Probable Cause Similarity: {similarity['Probable_Cause_Similarity']}\n")

            output_file.write("\n")


# Define paths

json_path = "C:\\Users\\olaye\\Documents\\final_extracted_data.json"

output_txt_path = "C:\\Users\\olaye\\Documents\\similarities.txt"


# Run the script

find_similarities(json_path, output_txt_path)