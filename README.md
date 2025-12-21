# Grammatical Error Checker (for Persian)

<p>
  This project uses the Python 3.8+ Hazm NLP toolkit to process given tokens and a set of rules based on Farsi grammar to correct possible Farsi grammatical errors in simple and short sentences. Simple mistakes such as wrong sentence parts order or unmatching subject and verb identifiers are detected and corrected. As long as it falls within the cases provided in the ruleset, it will correct the mistakes and record the original and corrected versions in the log.json file.
</p>

<p>
  <strong>Note:</strong> The method is outdated in the current state of things. For better accuracy, consider using a fine-tuned BERT model or LLM API for this particular task.
</p>

## Features

- **Persian Grammar Correction**: Detects and corrects common grammatical errors in Persian text
- **Web Interface**: Flask-based web application for easy interaction
- **Command-line Processing**: Script for batch processing text files
- **Comprehensive Logging**: Records original and corrected sentences in JSON format
- **Sentence Structure Analysis**: Parses Persian sentences into components (subject, verb, object, etc.)
- **Verb Conjugation**: Corrects verb forms based on subject and tense
- **Normalization**: Uses Hazm's normalization for consistent text processing

## Project Structure

```
Grammatical-error-checker/
├── app.py                  # Flask web application
├── main.py                 # Command-line processing script
├── grammarchecker.py       # Core grammar checking logic
├── hazm_methods.py         # Extended Hazm functionality
├── README.md               # Project documentation
├── requirements.txt        # Python dependencies
├── sample_text.txt         # Sample input text
├── log.json                # Output log file
├── //resources//adverbs.txt             # List of Persian adverbs
├── //resources//LinkingVerbs.txt        # List of Persian linking verbs
├── static/                 # Static files (CSS, fonts)
├── templates/              # HTML templates
└── resources/              # NLP model files
```

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-repo/grammatical-error-checker.git
   cd grammatical-error-checker
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure you have the Hazm library and Flask module installed. The main dependencies are:
   - `hazm` - Persian NLP toolkit
   - `flask` - Web framework

## Usage

### Web Application

To run the web interface:

```bash
python app.py
```

Then open your browser and navigate to `http://127.0.0.1:5000`. The web interface allows you to:

- Enter Persian text directly in the text box
- Upload a text file for processing
- View the corrected output
- Download the results

### Command-line Processing

To process a text file using the command-line script:

```bash
python main.py
```

This will:
1. Read from `sample_text.txt`
2. Process each line through the grammar checker
3. Write results to `log.json`
4. Display progress messages

### Input/Output

- **Input**: Persian text (either through web interface or text file)
- **Output**: Corrected Persian text with proper grammar
- **Log File**: `log.json` contains entries with original and corrected sentences

## Core Components

### grammarchecker.py

The heart of the system with these key classes:

- **PersianGrammarChecker**: Main class that handles grammar correction
- **VerbTense**: Enum for Persian verb tenses (18 different tenses)
- **SentenceComponents**: Data structure for parsed sentence parts
- **SentenceFlags**: Boolean flags for sentence structure
- **VerbProperties**: Properties describing verb forms

Key features:
- Sentence parsing and component extraction
- Verb tense detection and correction
- Subject-verb agreement checking
- Adverb classification
- Sentence reconstruction with correct grammar

### app.py

Flask web application with:
- `/` route: Main page with input form
- `/process` route: Handles text processing (both text input and file upload)
- Text normalization using Hazm
- Sentence tokenization
- Grammar correction
- Logging to `log.json`

### main.py

Command-line processing script that:
- Reads from `sample_text.txt`
- Processes each line through the grammar checker
- Writes results to `log.json`
- Handles file operations with error checking

## Technical Details

### Grammar Correction Process

1. **Normalization**: Text is normalized using Hazm's normalizer
2. **Tokenization**: Sentences are split into tokens
3. **POS Tagging**: Parts of speech are identified
4. **Sentence Parsing**: Components (subject, verb, object, etc.) are extracted
5. **Verb Analysis**: Verb tense and properties are determined
6. **Correction**: Appropriate verb forms are selected based on subject
7. **Reconstruction**: Corrected sentence is built from components

### Supported Verb Tenses

The system handles 18 Persian verb tenses:
- Past tenses (perfective, imperfective, progressive, etc.)
- Present tenses (perfective, imperfective, subjunctive, etc.)
- Future tenses
- Passive forms
- Negative forms

### Limitations

- Works best with simple, short sentences
- May misunderstand already correct sentences due to similar verb forms
- Rule-based approach has limitations compared to modern ML approaches
- Requires proper Persian text input (no mixed languages)

## Credits

- **Hazm NLP Toolkit**: Developed by Roshan Research - https://github.com/roshan-research/hazm
- **Flask**: Web framework - https://flask.palletsprojects.com/

## License

MIT

## Future Improvements

- Add more comprehensive grammar rules
- Improve verb tense detection accuracy
- Add support for complex sentence structures
- Implement machine learning for better accuracy
- Add user interface improvements
- Support for batch processing multiple files

## Contact

For questions or issues, please contact me through telegram @s0hell.
