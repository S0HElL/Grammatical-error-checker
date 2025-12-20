from grammarchecker import PersianGrammarChecker
from hazm_methods import parser as p, SentenceTokenizer
from hazm import Normalizer


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

# generating the final output
if text:
    with open("log.json", "a", encoding="utf-8") as f:
        for line in text:
            # Normalize the line first
            normalized_line = normalizer.normalize(line.strip())
            
            # Tokenize the normalized line into sentences
            sentences = sentence_tokenizer.tokenize(normalized_line)
              
            # Process each sentence individually
            for sentence in sentences:
                if sentence.strip():  # Skip empty sentences
                    corrected_line = gc.correct(sentence.strip())
                    import json
                    output = {
                        "corrected": corrected_line,
                        "original": sentence.strip()
                    }
                    f.write(json.dumps(output, ensure_ascii=False) + "\n")
            
            
            

#بستن فایل
try:
    file.close()
    print("File closed successfully.")
except Exception as e:
    print(f"Error closing file: {e}")



