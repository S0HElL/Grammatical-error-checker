# Grammatical-error-checker (for Persian)
<p>
  This project uses the Python 3.8+ Hazm NLP toolkit to process given tokens and a set of rules based on Farsi grammar provided by me to correct possible Farsi grammatical errors in simple and short sentences.   
Simple Mistakes such as wrong sentence parts order or unmatching subject and verb identifiers. As long as it falls in the cases provied in ruleset it will correct the mistakes and record the original and the correct version in the log.txt. Beware however it might misunderstand and try to correct already correct sentences as a handful of Persian verbs have similar forms while having diferent verb identifiers.   
</p>
<p>
The method is outdated in the current state of things, better use a finetuned BERT model or LLM api for this particular task.
</p>
<p>
The webapp was written using the Flask framework.      
You will need the Hazm library and Flask module to run the code. Open a terminal and Use ``pip install -r requirements.txt`` to install them on your machine and you're good to go.    
note: currently it only works with python version 3.11 .
because of spaCy having problems with 3.12+.
</p>
Credits to roshan research for the toolkit. https://github.com/roshan-research/hazm  


