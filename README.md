# Grammatical-error-checker
This project uses the Python 3.8+ Hazm nlp toolkit to process given tokens and and a set of rules based on Farsi grammar provided by me to correct possible Farsi grammatical errors in simple and short sentences.   

Simple Mistakes such as wrong sentence parts order or unmatching subject and verb identifiers. As long as it falls in the cases provied in ruleset it will correct the mistakes and record the original and the correct version in the log.txt. Beware however it might misunderstand and try to correct already correct sentences as a handful of Persian verbs have similar forms while having diferent verb identifiers.   

I originally planned to use this project to generate cases to provide learning material for a language model. If you don't know Farsi or Have no idea for the input you can run the case generator and give the output to the main app.
The webapp was written using the Flask framework.      

You will need the Hazm library and Flask module to run the code. Open a terminal and Use ``pip install -r requirements.txt`` to install them on your machine and you're good to go.     

Credits to roshan research for the library. https://github.com/roshan-research/hazm  

If you have any questions you can contact me on telegram.
