from flask import Flask, render_template, request, redirect, url_for
from filehandler import open_file, close_file
from grammarchecker import grammarchecker as gc
from hazm_methods import parser as p

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():

    input_text = request.form.get('input_text')
    result = ''

    # Write the log
    with open("app_log.txt", "a", encoding="utf-8") as f:
        for line in input_text.splitlines():
            corrected_line = gc.correction(line.strip())
            f.write("Corrected: {" + corrected_line + "}\nOriginal: {" + line.strip() + "}\n")

    # Check if input_text is provided (text box input)
    if input_text:
        for line in input_text.splitlines():
            result += gc.correction(line) + '\n'
        return render_template('index.html', result=result.strip(), input_text=input_text, input_type='Text Box Input')

    # Check if file is uploaded (file input)
    if 'file' in request.files:
        file = request.files['file']

        # Check if the file has a valid name and is not empty
        if file and file.filename:
            with file.stream as f:  # Use with statement to properly close the file
                input_text = f.read().decode('utf-8')

            result = " ".join(gc.correction(sentence) for sentence in p.getsenttokens(input_text))
            return render_template('index.html', result=result.strip(), input_text=input_text, input_type='File Input')

    # Redirect to the index page if no valid input is provided
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)
