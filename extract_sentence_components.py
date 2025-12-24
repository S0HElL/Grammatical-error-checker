from grammarchecker import get_grammar_checker

def extract_sentence_components(sentence: str):
    """
    Takes a Persian sentence and returns the extracted sentence components.

    Args:
        sentence (str): The input Persian sentence.

    Returns:
        SentenceComponents: An object containing the parsed components like subject, verb, object, etc.
    """
    checker = get_grammar_checker()
    return checker.extract_components(sentence)

# Example usage
if __name__ == "__main__":
    sentence = "من به‌همراه حسین، رضا را ملاقات‌کردیم"
    components = extract_sentence_components(sentence)
    with open("sentence_components.txt", "w", encoding="utf-8") as f:
        f.write(f"Input Sentence:{sentence}\n")
        f.write(f"Subject: {components.subject}\n")
        f.write(f"Verb: {components.verb}\n")
        f.write(f"Object: {components.object}\n")
        f.write(f"Complement: {components.complement}\n")
        f.write(f"Adposition: {components.adposition}\n")
        f.write(f"Adverbs: {components.adverbs}\n")
        f.write(f"Untagged words: {components.untagged_words}\n")