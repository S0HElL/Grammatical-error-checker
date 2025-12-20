from flask import Flask, render_template, request, redirect, url_for
from grammarchecker import PersianGrammarChecker
from hazm_methods import SentenceTokenizer
from hazm import Normalizer
import json

app = Flask(__name__)

# Initialize components
normalizer = Normalizer()
grammar_checker = PersianGrammarChecker()
sentence_tokenizer = SentenceTokenizer()


def process_text(text: str) -> tuple[str, list[dict]]:
    """
    Process text through grammar checker.
    Returns: (corrected_text, log_entries)
    """
    if not text or not text.strip():
        return '', []
    
    corrected_sentences = []
    log_entries = []
    
    # Split into lines first, then tokenize each line into sentences
    for line in text.splitlines():
        if not line.strip():
            continue
            
        # Normalize the line
        normalized_line = normalizer.normalize(line.strip())
        
        # Tokenize into sentences
        sentences = sentence_tokenizer.tokenize(normalized_line)
        
        # Process each sentence
        for sentence in sentences:
            if sentence.strip():
                corrected = grammar_checker.correct(sentence.strip())
                corrected_sentences.append(corrected)
                
                # Create log entry
                log_entries.append({
                    "original": sentence.strip(),
                    "corrected": corrected
                })
    
    # Join corrected sentences with space
    result = ' '.join(corrected_sentences)
    
    return result, log_entries


def write_log(log_entries: list[dict]):
    """Write log entries to log.json file"""
    try:
        with open("log.json", "a", encoding="utf-8") as f:
            for entry in log_entries:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"Error writing to log file: {e}")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process():
    input_text = request.form.get('input_text', '').strip()
    uploaded_file = request.files.get('file')
    
    # Determine input source
    if uploaded_file and uploaded_file.filename:
        # File upload takes precedence
        try:
            input_text = uploaded_file.read().decode('utf-8')
            input_type = 'File Input'
        except Exception as e:
            return render_template(
                'index.html',
                result=f"Error reading file: {e}",
                input_text='',
                input_type='Error'
            )
    elif input_text:
        # Text box input
        input_type = 'Text Box Input'
    else:
        # No valid input
        return redirect(url_for('index'))
    
    # Process the text
    corrected_text, log_entries = process_text(input_text)
    
    # Write to log
    write_log(log_entries)
    
    # Return results
    return render_template(
        'index.html',
        result=corrected_text,
        input_text=input_text,
        input_type=input_type
    )


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)