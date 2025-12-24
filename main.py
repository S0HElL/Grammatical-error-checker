from grammarchecker import PersianGrammarChecker
from hazm_methods import parser as p, SentenceTokenizer
from hazm import Normalizer
import concurrent.futures
import json


#objects
try:
    file = open("sample_text.txt", "r", encoding="utf-8")
    print("File 'sample_text.txt' opened successfully.")
except Exception as e:
    print(f"Error opening file 'sample_text.txt': {e}")
    file = None

# Initialize normalizer, grammar checker and sentence tokenizer
normalizer = Normalizer()
gc = PersianGrammarChecker()
sentence_tokenizer = SentenceTokenizer()

if file is None:
    print("Error: Could not open file")
    exit(1)

text = file.readlines()

# Collect all sentences into a list
all_sentences = []
for line in text:
    normalized_line = normalizer.normalize(line.strip())
    sentences = sentence_tokenizer.tokenize(normalized_line)
    for sentence in sentences:
        if sentence.strip():  # Skip empty sentences
            all_sentences.append(sentence.strip())

# Process sentences in parallel using ThreadPoolExecutor
def process_sentence(sentence):
    corrected_line = gc.correct(sentence)
    return {
        "corrected": corrected_line,
        "original": sentence
    }

# Use ThreadPoolExecutor to process sentences in parallel
with concurrent.futures.ThreadPoolExecutor() as executor:
    results = list(executor.map(process_sentence, all_sentences))

# Write results to log.json atomically
with open("log.json", "a", encoding="utf-8") as f:
    for result in results:
        f.write(json.dumps(result, ensure_ascii=False) + "\n")

#بستن فایل
try:
    file.close()
    print("File closed successfully.")
except Exception as e:
    print(f"Error closing file: {e}")



