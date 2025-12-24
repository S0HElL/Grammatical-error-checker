from hazm_methods import parser as p
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from enum import Enum

class VerbTense(Enum):
    """Persian verb tenses"""
    NEGATIVE_IMPERFECTIVE_PAST = 'negative_imperfective_past'
    IMPERFECTIVE_PAST = 'imperfective_past'
    NEGATIVE_PERFECTIVE_PAST = 'negative_pefective_past'
    PASSIVE_PERFECTIVE_PAST = 'passive_perfective_past'
    NEGATIVE_PASSIVE_PERFECTIVE_PAST = 'negative_passive_perfective_past'
    PERFECTIVE_PAST = 'perfective_past'
    PROGRESSIVE_PAST = 'progressive_past'
    PAST_PRECEDENT = 'past_precedent'
    NEGATIVE_PAST_PRECEDENT = 'negative_past_precedent'
    PERFECTIVE_FUTURE = 'perfective_future'
    NEGATIVE_PERFECTIVE_FUTURE = 'negative_perfective_future'
    NEGATIVE_IMPERFECTIVE_PRESENT = 'negative_imperfective_present'
    IMPERFECTIVE_PRESENT = 'imperfective_present'
    SUBJUNCTIVE_PERFECTIVE_PRESENT = 'subjunctive_perfective_present'
    PASSIVE_PERFECTIVE_PRESENT = 'passive_perfective_present'
    NEGATIVE_PASSIVE_PERFECTIVE_PRESENT = 'negative_passive_perfective_present'
    NEGATIVE_PERFECTIVE_PRESENT = 'negative_pefective_present'
    PERFECTIVE_PRESENT = 'perfective_present'
    PROGRESSIVE_PRESENT = 'progressive_present'


@dataclass
class SentenceComponents:
    """Container for parsed sentence components"""
    subject: str = ''
    verb: str = ''
    object: str = ''
    complement: str = ''
    adposition: str = ''
    noun_complement: str = ''
    noun_clause: str = ''
    adverbs: List[str] = field(default_factory=list)
    starting_adverb: str = ''
    verb_adverb: str = ''
    untagged_words: List[str] = field(default_factory=list)
    final_punctuation: str = '' 
    
    def __post_init__(self):
        pass
    
@dataclass
class SentenceFlags:
    """Boolean flags for sentence structure"""
    subject_found: bool = False
    subject_is_plural: bool = False
    verb_found: bool = False
    noun_complement_found: bool = False
    complement_found: bool = False
    object_found: bool = False
    noun_clause_found: bool = False
    verb_part_found: bool = False
    linking_verb: bool = False
    starting_adverb_found: bool = False
    verb_adverb_found: bool = False


@dataclass
class VerbProperties:
    """Properties describing the verb form"""
    is_present: bool
    is_negative: bool
    is_imperfective: bool
    is_subjunctive: bool
    is_future: bool
    is_passive: bool
    is_precedent: bool
    is_progressive: bool
    
    def to_tense(self) -> str:
        """Convert verb properties to tense string"""
        tense_map = {
            (False, True, True, False, False, False, False, False): VerbTense.NEGATIVE_IMPERFECTIVE_PAST,
            (False, False, True, False, False, False, False, False): VerbTense.IMPERFECTIVE_PAST,
            (False, True, False, False, False, False, False, False): VerbTense.NEGATIVE_PERFECTIVE_PAST,
            (False, False, False, False, True, False, False, False): VerbTense.PASSIVE_PERFECTIVE_PAST,
            (False, True, False, False, True, False, False, False): VerbTense.NEGATIVE_PASSIVE_PERFECTIVE_PAST,
            (False, False, False, False, False, False, False, False): VerbTense.PERFECTIVE_PAST,
            (False, False, False, False, False, False, False, True): VerbTense.PROGRESSIVE_PAST,
            (False, False, False, False, False, False, True, False): VerbTense.PAST_PRECEDENT,
            (False, True, False, False, False, False, True, False): VerbTense.NEGATIVE_PAST_PRECEDENT,
            (None, False, False, False, False, True, False, False): VerbTense.PERFECTIVE_FUTURE,
            (None, True, False, False, False, True, False, False): VerbTense.NEGATIVE_PERFECTIVE_FUTURE,
            (True, True, True, False, False, False, False, False): VerbTense.NEGATIVE_IMPERFECTIVE_PRESENT,
            (True, False, True, False, False, False, False, False): VerbTense.IMPERFECTIVE_PRESENT,
            (True, False, False, True, False, False, False, False): VerbTense.SUBJUNCTIVE_PERFECTIVE_PRESENT,
            (True, False, False, False, True, False, False, False): VerbTense.PASSIVE_PERFECTIVE_PRESENT,
            (True, True, False, False, True, False, False, False): VerbTense.NEGATIVE_PASSIVE_PERFECTIVE_PRESENT,
            (True, True, False, False, False, False, False, False): VerbTense.NEGATIVE_PERFECTIVE_PRESENT,
            (True, False, False, False, False, False, False, False): VerbTense.PERFECTIVE_PRESENT,
            (True, False, False, False, False, False, False, True): VerbTense.PROGRESSIVE_PRESENT,
        }
        
        key = (
            self.is_present if not self.is_future else None,
            self.is_negative,
            self.is_imperfective,
            self.is_subjunctive,
            self.is_passive,
            self.is_future,
            self.is_precedent,
            self.is_progressive
        )
        
        tense = tense_map.get(key)
        return tense.value if tense else ''


class PersianGrammarChecker:
    """Persian grammar checker with rule-based correction"""
    
    # Sorted by length descending to match longest suffixes first
    PERSON_IDENTIFIERS = sorted(['م', 'ی', 'ه', 'یم', 'ید', 'ند'], key=len, reverse=True)
    PRONOUNS = ['من', 'تو', 'او', 'ما', 'شما', 'آنها']
    
    def __init__(self):
        self.linking_verbs = self._load_linking_verbs()
        self.adverbs = self._load_adverbs()
    
    def _load_linking_verbs(self) -> set:
        try:
            with open("//resources//LinkingVerbs.txt", "r", encoding="utf-8") as f:
                return {line.strip() for line in f}
        except FileNotFoundError:
            return set()
    
    def _load_adverbs(self) -> set:
        try:
            with open("//resources//adverbs.txt", "r", encoding="utf-8") as f:
                return {line.strip() for line in f}
        except FileNotFoundError:
            return set()
    
    def _is_plural_noun(self, noun: str) -> bool:
        if noun.endswith("ها") or noun.endswith("های"):
            return True
        if noun.endswith("ان") and p.stemmer(noun) != noun:
            return True
        return False
    
    def _is_linking_verb(self, verb: str) -> bool:
        # Check if the verb itself is in linking verbs
        if any(verb in linking_verb for linking_verb in self.linking_verbs):
            return True
        
        # Check if the lemmatized form is in linking verbs
        lemmatized = p.lemmatizer(verb).split('#')[0]
        return any(lemmatized in linking_verb for linking_verb in self.linking_verbs)
    
    def _classify_adverbs(self, adverbs: List[str]) -> Tuple[str, str]:
        starting_adverb = ''
        verb_adverb = ''

        for adverb in adverbs:
            if adverb in self.adverbs:
                starting_adverb = adverb
            else:
                verb_adverb = adverb

        return starting_adverb, verb_adverb
    
    def _extract_verb_stem(self, verb: str) -> Tuple[str, bool]:
        stem_result = p.lemmatizer(verb)
        parts = stem_result.split('#')
        
        for i, part in enumerate(parts):
            if part in verb:
                is_present = i > 0
                return part, is_present
        
        return parts[0] if parts else verb, False
    def _analyze_verb_properties(self, verb: str, is_present: bool, 
                                    is_linking: bool, is_verb_part: bool) -> VerbProperties:
            # Get the root lemma to distinguish main verbs from auxiliaries
            # e.g., 'budi' -> lemma 'bud'. 'rafte bud' -> lemma 'raft#row'
            lemma_full = p.lemmatizer(verb)
            lemma_past = lemma_full.split('#')[0]
            
            is_negative = verb.startswith("ن")
            is_imperfective = verb.startswith("نمی") or verb.startswith("می")
            is_subjunctive = verb.startswith("ب") and is_present
            is_future = verb.startswith("خواه")
            is_progressive = ('داشت' in verb or 'دار' in verb) and is_verb_part


            if 'بود' in verb and not self._is_linking_verb(verb):
                if lemma_past == 'بود': 
                    # If root is 'bud', it's only precedent if it looks like "bude..."
                    is_precedent = 'ه' in verb 
                else:
                    is_precedent = True
            else:
                is_precedent = False

            # Hazm treats these as compound active verbs. Applying Passive tense would double-passive them.
            if 'شد' in verb and not self._is_linking_verb(verb) and not is_future:
                if 'شد' in lemma_past:
                    # If the stem includes 'shod' (e.g. doktor_shod), treat as Active Compound.
                    is_passive = False
                else:
                    # Only true if 'shod' is on surface but not in stem (rare, but implies transformation)
                    is_passive = True
            else:
                is_passive = False
                
            if is_future:
                is_present = False
            
            return VerbProperties(
                is_present=is_present,
                is_negative=is_negative,
                is_imperfective=is_imperfective,
                is_subjunctive=is_subjunctive,
                is_future=is_future,
                is_passive=is_passive,
                is_precedent=is_precedent,
                is_progressive=is_progressive
            )
    def _strip_person_identifier(self, verb: str) -> str:
        """Remove person identifier suffix from verb safely"""
        lemma = p.lemmatizer(verb).split('#')[0]
        
        if verb == lemma and '\u200c' not in verb:
            return verb

        for identifier in self.PERSON_IDENTIFIERS:
            if verb.endswith(identifier):
                stripped = verb[:-len(identifier)]
                # Ensure we don't strip the whole word (simple sanity check)
                if len(stripped) > 1:
                    return stripped
        return verb
 
    def _select_correct_verb_form(self, subject: str, subject_is_plural: bool, 
                                   verb_list) -> str:
        if not isinstance(verb_list, list):
            return subject
        
        # Helper to check for precise pronoun match (avoids substring errors)
        def has_pronoun(pronoun_to_check, text):
            # Check exact match or word boundaries
            return (pronoun_to_check == text or 
                    f" {pronoun_to_check} " in f" {text} " or 
                    text.startswith(f"{pronoun_to_check} ") or 
                    text.endswith(f" {pronoun_to_check}"))

        # Explicitly check 'shoma' first or ensure precise matching
        for i, pronoun in enumerate(self.PRONOUNS):
            if has_pronoun(pronoun, subject):
                # Logic for shifting to plural form
                if subject_is_plural and i + 3 <= 5:
                    return verb_list[i + 3]
                else:
                    return verb_list[i]
        
        # Fallbacks
        if subject_is_plural:
            return verb_list[5] if len(verb_list) > 5 else verb_list[0]
        else:
            return verb_list[2] if len(verb_list) > 2 else verb_list[0] 
    
    def _parse_sentence_components(self, tags: List[Tuple[str, str]]) -> Tuple[SentenceComponents, SentenceFlags]:
        components = SentenceComponents()
        flags = SentenceFlags()
        
        for tag in tags:
            word, pos = tag
            components.untagged_words.append(word)
         
        for i, tag in enumerate(tags):
            word, pos = tag
            next_tag = tags[i + 1] if i + 1 < len(tags) else None
            prev_tag = tags[i - 1] if i - 1 >= 0 else None
            
            # Check for PUNCT (Universal) or PUNC (Legacy)
            if pos in ['PUNCT', 'PUNC']:
                # Check for Persian (؟، ؛) and English punctuation
                if word in ['?', '!', '.', ';', '؟', '؛']:
                    components.final_punctuation = word
                
                # Remove punctuation from the generic word pool so it doesn't float
                if word in components.untagged_words:
                    components.untagged_words.remove(word)

            elif pos in ['ADP', 'ADP,EZ']:
                self._handle_adposition(word, next_tag, components, flags)
            
            elif pos in ['PRON', 'NOUN', 'NOUN,EZ']:
                self._handle_noun_or_pronoun(word, next_tag, components, flags)
            elif pos == 'DET':
                self._handle_determiner(word, next_tag, components, flags)
            elif pos == 'CCONJ':
                self._handle_conjunction(word, next_tag, prev_tag, components, flags)
            elif pos == 'ADV':
                components.adverbs.append(word)
                if word in components.untagged_words:
                    components.untagged_words.remove(word)
            elif pos in ['ADJ', 'ADJ,EZ']:
                self._handle_adjective(word, prev_tag, components, flags)
            elif pos == 'VERB':
                self._handle_verb(word, next_tag, prev_tag, components, flags)
            elif pos == 'SCONJ':
                self._handle_subordinating_conjunction(word, prev_tag, components)
        
        return components, flags
  
    def _handle_adposition(self, word: str, next_tag: Optional[Tuple[str, str]],
                          components: SentenceComponents, flags: SentenceFlags):
        if word == "را":
            return

        if next_tag and next_tag[1] in ['PRON', 'NOUN', 'NOUN,EZ', 'DET', 'ADJ', 'ADJ,EZ']:
            components.complement = next_tag[0]
            components.adposition = word
            flags.complement_found = True
            if word in components.untagged_words:
                components.untagged_words.remove(word)
            if next_tag[0] in components.untagged_words:
                components.untagged_words.remove(next_tag[0])
    def _handle_noun_or_pronoun(self, word: str, next_tag: Optional[Tuple[str, str]],
                                components: SentenceComponents, flags: SentenceFlags):
        if flags.complement_found and word == components.complement:
            return
        
        if next_tag and next_tag[0] == '!':
            components.noun_clause = word
            flags.noun_clause_found = True
            if word in components.untagged_words:
                components.untagged_words.remove(word)
         
        elif next_tag and next_tag[0] == 'را':
            components.object = word
            flags.object_found = True
            
            # Remove the object word itself
            if word in components.untagged_words:
                components.untagged_words.remove(word)
                
            if next_tag[0] in components.untagged_words:
                components.untagged_words.remove(next_tag[0])
         
        elif not flags.subject_found:
            components.subject = word
            flags.subject_found = True
            flags.subject_is_plural = self._is_plural_noun(word)
            if word in components.untagged_words:
                components.untagged_words.remove(word)
    def _handle_determiner(self, word: str, next_tag: Optional[Tuple[str, str]],
                          components: SentenceComponents, flags: SentenceFlags):
        if next_tag and next_tag[1] in ['PRON', 'NOUN', 'NOUN,EZ', 'ADJ', 'ADJ,EZ']:
            combined = f"{word} {next_tag[0]}"
            if flags.complement_found and word == components.complement:
                components.complement = combined
                if word in components.untagged_words:
                    components.untagged_words.remove(word)
    
    def _handle_conjunction(self, word: str, next_tag: Optional[Tuple[str, str]], 
                           prev_tag: Optional[Tuple[str, str]], 
                           components: SentenceComponents, flags: SentenceFlags):
        if not next_tag or next_tag[1] not in ['PRON', 'NOUN', 'NOUN,EZ']:
            return
        
        if flags.subject_found and prev_tag and prev_tag[0] == components.subject:
            components.subject = f"{components.subject} {word} {next_tag[0]}"
            flags.subject_is_plural = True
            if word in components.untagged_words:
                components.untagged_words.remove(word)
            if next_tag[0] in components.untagged_words:
                components.untagged_words.remove(next_tag[0])

        elif prev_tag and prev_tag[0] == components.complement:
            components.complement = f"{components.complement} {word} {next_tag[0]}"
            if word in components.untagged_words:
                components.untagged_words.remove(word)

        elif prev_tag and prev_tag[0] == components.object:
            components.object = f"{components.object} {word} {next_tag[0]}"
            if word in components.untagged_words:
                components.untagged_words.remove(word)
    
    def _handle_adjective(self, word: str, prev_tag: Optional[Tuple[str, str]],
                         components: SentenceComponents, flags: SentenceFlags):
        if prev_tag and prev_tag[0] == components.subject:
            components.subject = f"{components.subject} {word}"
            if word in components.untagged_words:
                components.untagged_words.remove(word)

        elif prev_tag and prev_tag[0] == components.object:
            components.object = f"{components.object} {word}"
            if word in components.untagged_words:
                components.untagged_words.remove(word)

        elif prev_tag and prev_tag[0] == components.complement:
            components.complement = f"{components.complement} {word}"
            if word in components.untagged_words:
                components.untagged_words.remove(word)

        elif flags.linking_verb:
            components.noun_complement = word
            flags.noun_complement_found = True
            if word in components.untagged_words:
                components.untagged_words.remove(word)

    def _handle_verb(self, word: str, next_tag: Optional[Tuple[str, str]],
                        prev_tag: Optional[Tuple[str, str]],
                        components: SentenceComponents, flags: SentenceFlags):
            if not flags.verb_found:
                components.verb = word
                flags.verb_found = True
                flags.linking_verb = self._is_linking_verb(word)

            if next_tag and next_tag[1] == 'VERB':
                components.verb = f"{components.verb}_{next_tag[0]}"
                flags.verb_part_found = True
                if next_tag[0] in components.untagged_words:
                    components.untagged_words.remove(next_tag[0])

            if (prev_tag and flags.verb_found and prev_tag[1] in ['NOUN', 'NOUN,EZ']
                and prev_tag[0] not in components.complement
                and prev_tag[0] not in components.object
                and prev_tag[0] not in components.subject): # <--- THIS LINE WAS ADDED

                if flags.linking_verb:
                    components.noun_complement = prev_tag[0]
                    flags.noun_complement_found = True
                    if prev_tag[0] in components.untagged_words:
                        components.untagged_words.remove(prev_tag[0])
                else:
                    # For compound verbs: the noun part becomes part of the verb
                    components.verb = f"{prev_tag[0]}_{components.verb}"
                    flags.verb_part_found = True
                    if prev_tag[0] in components.untagged_words:
                        components.untagged_words.remove(prev_tag[0])

            if word in components.untagged_words:
                components.untagged_words.remove(word)
      
    def _handle_subordinating_conjunction(self, word: str, prev_tag: Optional[Tuple[str, str]],
                                        components: SentenceComponents):
        if not prev_tag:
            return

        if prev_tag[0] in components.subject:
            components.subject = f"{components.subject} {word}"
            if word in components.untagged_words:
                components.untagged_words.remove(word)

        elif prev_tag[0] in components.complement:
            components.complement = f"{components.complement} {word}"
            if word in components.untagged_words:
                components.untagged_words.remove(word)
        
    def _remove_duplicates(self, text: str) -> str:
        """Remove consecutive duplicate words from text"""
        words = text.split()
        if not words:
            return text
        
        cleaned_words = [words[0]]
        for i in range(1, len(words)):
            if words[i] != words[i-1]:
                cleaned_words.append(words[i])
        
        return ' '.join(cleaned_words)

    def extract_components(self, text: str) -> SentenceComponents:
        """Extract sentence components from text"""
        normalized_text = p.normalizer(text)
        tokens = p.getwordtokens(normalized_text)
        tags = p.tagger(tokens)

        components, flags = self._parse_sentence_components(tags)
        return components
    def _build_corrected_sentence(self, components: SentenceComponents,
                                    flags: SentenceFlags, corrected_verb: str) -> str:
        parts = []
        
        if flags.noun_clause_found:
            parts.append(f"{components.noun_clause}!")
        if flags.starting_adverb_found:
            parts.append(components.starting_adverb)
        if flags.subject_found:
            parts.append(components.subject)
            if components.untagged_words and not flags.verb_part_found:
                parts.append(' '.join(components.untagged_words).strip('.'))
        if flags.complement_found:
            parts.append(f"{components.adposition} {components.complement}")
        if flags.object_found:
            parts.append(f"{components.object} را")
        if flags.verb_adverb_found:
            parts.append(components.verb_adverb)
        if flags.noun_complement_found:
            parts.append(components.noun_complement)
        if flags.verb_found:
            parts.append(corrected_verb)
        
        sentence = ' '.join(parts)
        
        # Append the detected punctuation, otherwise default to fullstop
        if components.final_punctuation:
             sentence += components.final_punctuation
        else:
             sentence += '.'
        
        return self._remove_duplicates(sentence)
   
    def correct(self, text: str) -> str:
        """Main method to correct Persian grammar in text"""
        # Normalize the text (which includes separating compound words)
        normalized_text = p.normalizer(text)
        tokens = p.getwordtokens(normalized_text)
        tags = p.tagger(tokens)
        
        components, flags = self._parse_sentence_components(tags)
        
        if not flags.verb_found:
            return text
        
        verb = components.verb
        
        # Handle compound verbs splitting
        if flags.verb_part_found and '_' in verb:
            parts = verb.split('_')
            noun_part = parts[0]
            verb_part = parts[1]
            
            # Safe strip only on the actual verb part
            verb_part_cleaned = self._strip_person_identifier(verb_part)
            
            # Reconstruct for stem extraction
            verb = f"{noun_part}_{verb_part_cleaned}"
        else:
            # Safe strip on simple verb
            verb = self._strip_person_identifier(verb)
        
        stem, is_present = self._extract_verb_stem(verb)
        
        verb_props = self._analyze_verb_properties(
            verb, is_present, flags.linking_verb, flags.verb_part_found
        )
        
        tense = verb_props.to_tense()
        if not tense:
            return text
        
        # Pass the full stem (including noun part for compound verbs) to conjugation
        verb_list = p.conjugation(stem, tense)

        if verb_list is None:
            corrected_verb = components.verb.replace("_", "‌")
        else:
            corrected_verb = self._select_correct_verb_form(
                components.subject, flags.subject_is_plural, verb_list
            )
            corrected_verb = corrected_verb.replace("_", "‌")
        
        starting_adverb, verb_adverb = self._classify_adverbs(components.adverbs)
        components.starting_adverb = starting_adverb
        components.verb_adverb = verb_adverb
        flags.starting_adverb_found = bool(starting_adverb)
        flags.verb_adverb_found = bool(verb_adverb)
        
        corrected_sentence = self._build_corrected_sentence(components, flags, corrected_verb)
        
        # Normalize the final result using regular normalizer before returning
        normalized_result = p.normalizer(corrected_sentence)
        
        return normalized_result.replace("  ", " ")


# Singleton instance of PersianGrammarChecker
_grammar_checker_instance = None

def get_grammar_checker():
    """Get singleton instance of PersianGrammarChecker"""
    global _grammar_checker_instance
    if _grammar_checker_instance is None:
        _grammar_checker_instance = PersianGrammarChecker()
    return _grammar_checker_instance

def correction(text: str) -> str:
    """Legacy function for backward compatibility"""
    checker = get_grammar_checker()
    return checker.correct(text)