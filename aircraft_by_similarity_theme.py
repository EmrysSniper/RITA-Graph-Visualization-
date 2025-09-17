import json
from pathlib import Path

# Load the JSON file
input_path = Path("C:\\Users\\olaye\\Documents\\UARC\\final_aircraft_section_cleaned.json")
output_path = Path("C:\\Users\\olaye\\Documents\\UARC\\cleaned_aircraft_data.json")



# Define the sentences to remove from the Stall / Stall_spin section
stall_spin_sentences = [
    "000ft above mean sea level  when he established contact with the pilot of another airplane",
    "The   pilot stated that he was making position reports during cruise flight about 1",
    "The  descended uncontrolled into the river.",
    "a  and a",
    "and a non- active secondary frequency 135.25 Mhz in his transceiver at the time of the collision.",
    "and it could not be determined whether the pilot of the   was monitoring the CTAF or making position reports.",
    "reported that he had a primary active radio frequency of 122.90 Mhz",
    "the  continued to fly",
    "According to the  single-engine performance chart"
]

# Define the sentence to remove from the Spatial disorientation section
spatial_disorientation_sentence = "at 0650 am mountain daylight time"

# Load the JSON data
with open(input_path, encoding = "utf=8") as file:
    data = json.load(file)

# Clean the Stall / Stall_spin section
data["Stall / Stall_spin"] = [
    item for item in data["Stall / Stall_spin"]
    if item not in stall_spin_sentences
]

# Clean the Spatial disorientation section
data["Spatial disorientation"] = [
    item for item in data["Spatial disorientation"]
    if item != spatial_disorientation_sentence
]

# Save the cleaned data back to a new JSON file
with open(output_path, 'w', encoding = "utf-8") as file:
    json.dump(data, file, indent=4)

print("Cleaned data has been saved to 'cleaned_aircraft_data.json'")
