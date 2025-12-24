from hazm_methods import parser as p
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from enum import Enum
import re

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
        
        # Future overrides present check in key generation
        p_val = self.is_present if not self.is_future else None

        key = (
            p_val,
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
    
    PERSON_IDENTIFIERS = sorted(['م', 'ی', 'ه', 'یم', 'ید', 'ند'], key=len, reverse=True)
    PRONOUNS = ['من', 'تو', 'او', 'ما', 'شما', 'آنها']
    # Compound verbs that use 'dashtan' (to have) as a root but are NOT progressive auxiliary
    NON_PROGRESSIVE_COMPOUNDS = ['دوست', 'احتمال', 'نیاز', 'انتظار', 'خبر', 'باور', 'یاد'] 
    
    def __init__(self):
        self.linking_verbs = self._load_linking_verbs()
        self.adverbs = self._load_adverbs()
    
    def _load_linking_verbs(self) -> set:
        try:
            with open("//resources//LinkingVerbs.txt", "r", encoding="utf-8") as f:
                return {line.strip() for line in f}
        except FileNotFoundError:
            return {'است', 'بود', 'شد', 'هست', 'نیست', 'باش', 'بودن'}
    
    def _load_adverbs(self) -> set:
        try:
            with open("//resources//adverbs.txt", "r", encoding="utf-8") as f:
                return {line.strip() for line in f}
        except FileNotFoundError:
            return {'دیروز', 'امروز', 'فردا', 'خوب', 'بد', 'سریع', 'آهسته', 'همیشه', 'هرگز', 'زود'}
    
    def _is_plural_noun(self, noun: str) -> bool:
        if noun.endswith("ها") or noun.endswith("های"):
            return True
        
        if noun.endswith("ان"):
            # 1. Whitelist of singular words ending in 'an'
            singular_exceptions = {
                'باران', 'تهران', 'ایران', 'آسمان', 'زمستان', 'تابستان', 
                'داستان', 'دندان', 'زبان', 'جهان', 'جان', 'نان', 'لیوان',
                'کیهان', 'طوفان', 'جریان', 'درمان', 'فرمان', 'خیابان', 
                'بیابان', 'کوهستان', 'دبیرستان', 'بیمارستان', 'استان'
            }
            if noun in singular_exceptions:
                return False
            
            # 2. Use Lemmatizer (Dictionary) instead of Stemmer (Algorithmic)
            # Stemmer maps 'Baran' -> 'Bar' (Load), causing false plural detection.
            # Lemmatizer maps 'Baran' -> 'Baran' (Rain), preserving singularity.
            lemma = p.lemmatizer(noun).split('#')[0]
            if lemma != noun:
                return True
                
        return False
    
    def _is_linking_verb(self, verb: str) -> bool:
        if any(verb in linking_verb for linking_verb in self.linking_verbs):
            return True
        lemmatized = p.lemmatizer(verb).split('#')[0]
        # Specific check for Budan/Hastan roots
        if lemmatized in ['بود', 'هست', 'باش']:
            return True
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
    
    def _clean_stem(self, stem: str, is_present: bool) -> str:
        """
        Aggressively strips prefixes (mi, nemi, bi, na) from the stem 
        BEFORE sending to conjugation to prevent double prefixes like 'mimiroyam'.
        """
        s = stem.replace('\u200c', '')
        
        if s.startswith('نمی'):
            s = s[3:]
        elif s.startswith('می'):
            s = s[2:]
        elif s.startswith('ن') and not is_present: 
            s = s[1:]
        elif s.startswith('ب') and is_present: 
            s = s[1:]
            
        return s

    def _analyze_verb_properties(self, verb: str, full_lemma: str, 
                                 is_linking: bool, is_verb_part: bool,
                                 noun_part: str = '') -> VerbProperties:
            """
            Enhanced analysis to correctly identify tense, ignoring 'dashtan' 
            in non-progressive compounds.
            """
            lemma_parts = full_lemma.split('#')
            lemma_past = lemma_parts[0]
            
            is_negative = verb.startswith("ن")
            is_imperfective = "می" in verb or "نمی" in verb
            is_future = "خواه" in verb
            
            # Subjunctive: Starts with 'Be' usually in present stem
            is_subjunctive = verb.startswith("ب") and not is_imperfective
            
            # Heuristic for present tense
            is_present = False
            if len(lemma_parts) > 1 and lemma_parts[1] in verb.replace('\u200c', ''):
                 is_present = True
            elif "خواه" in verb:
                 is_present = False
            elif not is_future:
                # If surface contains the past root, it's likely past
                if lemma_past in verb.replace('\u200c', ''):
                    is_present = False
                else:
                    is_present = True

            #Progressive Check: blacklist "doost daram", "ehteram daram", etc.
            is_progressive = False
            if ('داشت' in verb or 'دار' in verb) and is_verb_part:
                if noun_part and any(x in noun_part for x in self.NON_PROGRESSIVE_COMPOUNDS):
                    is_progressive = False
                else:
                    is_progressive = True

            if 'بود' in verb and not self._is_linking_verb(verb):
                 is_precedent = True # e.g. Bude ast
            else:
                 # Standard precedent check (Rafte ast)
                 is_precedent = 'ه' in verb and not is_present and not is_imperfective and not is_future

            # Passive Check
            is_passive = False
            if 'شد' in verb and not is_linking and not is_future:
                # If lemma itself contains shod (e.g. gom_shodan), it's active.
                if 'شد' not in lemma_past:
                    is_passive = True
                
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
 
    def _select_correct_verb_form(self, subject: str, subject_is_plural: bool, 
                                   verb_list) -> str:
        if not isinstance(verb_list, list) or not verb_list:
            return subject
        
        norm_subj = subject.strip()
        
        # Check specific pronouns
        if "من" == norm_subj or norm_subj.endswith(" من"): return verb_list[0]
        if "تو" == norm_subj or norm_subj.endswith(" تو"): return verb_list[1]
        if "او" == norm_subj: return verb_list[2]
        if "ما" == norm_subj or " و من" in norm_subj: return verb_list[3] 
        if "شما" == norm_subj or " و تو" in norm_subj: return verb_list[4]
        if "آنها" == norm_subj or "آن‌ها" == norm_subj: return verb_list[5]
        
        # Fallbacks
        if subject_is_plural:
            return verb_list[5] if len(verb_list) > 5 else verb_list[0]
        else:
            return verb_list[2] if len(verb_list) > 2 else verb_list[0] 
    
    def _parse_sentence_components(self, tags: List[Tuple[str, str]]) -> Tuple[SentenceComponents, SentenceFlags]:
        components = SentenceComponents()
        flags = SentenceFlags()
        
        # Collect all words initially to manage "untagged" list
        for tag in tags:
            word, pos = tag
            components.untagged_words.append(word)
         
        for i, tag in enumerate(tags):
            word, pos = tag
            next_tag = tags[i + 1] if i + 1 < len(tags) else None
            prev_tag = tags[i - 1] if i - 1 >= 0 else None
            
            if pos in ['PUNCT', 'PUNC']:
                if word in ['?', '!', '.', ';', '؟', '؛']:
                    components.final_punctuation = word
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
        
        #Post-Processing: Compound Verbs
        # If we have an untagged word right before the verb that wasn't claimed, it's likely part of the verb.
        if components.verb and components.untagged_words:
            verb_parts = components.verb.split('_')
            # Only if the verb doesn't already have a noun part attached via the loop
            if len(verb_parts) == 1 or (flags.verb_part_found and '_' not in components.verb):
                last_untagged = components.untagged_words[-1]
                # Heuristic: The untagged word is physically close to the end of the sentence
                # Ideally check index, but here we assume parsing order.
                if not flags.noun_complement_found and not flags.linking_verb:
                    # Merge into verb
                    components.verb = f"{last_untagged}_{components.verb}"
                    flags.verb_part_found = True
                    components.untagged_words.remove(last_untagged)

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
        
        # Noun Clause (Vocative: "Ali!")
        if next_tag and next_tag[0] == '!':
            components.noun_clause = word
            flags.noun_clause_found = True
            if word in components.untagged_words:
                components.untagged_words.remove(word)
         
        elif next_tag and next_tag[0] == 'را':
            components.object = word
            flags.object_found = True
            if word in components.untagged_words:
                components.untagged_words.remove(word)
            if next_tag[0] in components.untagged_words:
                components.untagged_words.remove(next_tag[0])
         
        elif not flags.subject_found:
            components.subject = word
            flags.subject_found = True
            flags.subject_is_plural = self._is_plural_noun(word) or word in ['ما', 'شما', 'آنها']
            if word in components.untagged_words:
                components.untagged_words.remove(word)

    def _handle_determiner(self, word: str, next_tag: Optional[Tuple[str, str]],
                          components: SentenceComponents, flags: SentenceFlags):
        if next_tag and next_tag[1] in ['PRON', 'NOUN', 'NOUN,EZ', 'ADJ', 'ADJ,EZ']:
            # Attach determiner to whatever follows it
            combined = f"{word} {next_tag[0]}"
            # We don't know yet if next_tag[0] is Subject/Object, so we just prep it? 
            # Actually, standard logic usually fills Subject/Object when hitting the Noun.
            # This logic updates the ALREADY found component if we are backtracking, 
            # OR we need to wait. 
            # Simplified: If we haven't found subject yet, this Det+Noun will be subject.
            pass 
            # Note: The original logic here was slightly flawed/recursive. 
            # For robustness, we will let the Noun handler pick up the noun, 
            # and here we just ensure the determiner isn't left 'untagged'.
            if word in components.untagged_words:
                components.untagged_words.remove(word)
            # We prepend it to the next noun in untagged handling or reconstruction if needed.
            # But strictly, simpler to just treat as untagged_word that gets placed before Subject?
            # Or better: Prepend to the component if the next word becomes a component.
    
    def _handle_conjunction(self, word: str, next_tag: Optional[Tuple[str, str]], 
                           prev_tag: Optional[Tuple[str, str]], 
                           components: SentenceComponents, flags: SentenceFlags):
        if not next_tag or next_tag[1] not in ['PRON', 'NOUN', 'NOUN,EZ']:
            return
        
        # safer check using 'in' to handle multi-word subjects
        if flags.subject_found and prev_tag and prev_tag[0] in components.subject:
            components.subject = f"{components.subject} {word} {next_tag[0]}"
            flags.subject_is_plural = True
            if word in components.untagged_words:
                components.untagged_words.remove(word)
            if next_tag[0] in components.untagged_words:
                components.untagged_words.remove(next_tag[0])

        elif prev_tag and prev_tag[0] in components.complement:
            components.complement = f"{components.complement} {word} {next_tag[0]}"
            if word in components.untagged_words:
                components.untagged_words.remove(word)

        elif prev_tag and prev_tag[0] in components.object:
            components.object = f"{components.object} {word} {next_tag[0]}"
            if word in components.untagged_words:
                components.untagged_words.remove(word)
    
    def _handle_adjective(self, word: str, prev_tag: Optional[Tuple[str, str]],
                         components: SentenceComponents, flags: SentenceFlags):
        if not prev_tag: return

        if prev_tag[0] in components.subject:
            components.subject = f"{components.subject} {word}"
            if word in components.untagged_words: components.untagged_words.remove(word)

        elif prev_tag[0] in components.object:
            components.object = f"{components.object} {word}"
            if word in components.untagged_words: components.untagged_words.remove(word)

        elif prev_tag[0] in components.complement:
            components.complement = f"{components.complement} {word}"
            if word in components.untagged_words: components.untagged_words.remove(word)

        elif flags.linking_verb and not flags.noun_complement_found:
            components.noun_complement = word
            flags.noun_complement_found = True
            if word in components.untagged_words: components.untagged_words.remove(word)

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

            # Compound verb handling inside handler
            if (prev_tag and flags.verb_found and prev_tag[1] in ['NOUN', 'NOUN,EZ', 'ADJ']
                and prev_tag[0] not in components.complement
                and prev_tag[0] not in components.object
                and prev_tag[0] not in components.subject):

                if flags.linking_verb:
                    components.noun_complement = prev_tag[0]
                    flags.noun_complement_found = True
                    if prev_tag[0] in components.untagged_words:
                        components.untagged_words.remove(prev_tag[0])
                else:
                    # Append as prefix to verb
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
        
    def _build_corrected_sentence(self, components: SentenceComponents,
                                    flags: SentenceFlags, corrected_verb: str) -> str:
        """
        Reorders sentence components to standard Persian SOV order:
        (Time) Subject (Object+Ra) (Indirect+Prep) (NounComp) Verb
        """
        parts = []
        
        # 1. Vocative / Noun Clause
        if flags.noun_clause_found:
            parts.append(f"{components.noun_clause}!")

        # 2. Starting Adverb (Time)
        if flags.starting_adverb_found:
            parts.append(components.starting_adverb)
        
        # 3. Subject
        if flags.subject_found:
            parts.append(components.subject)
            
        # 4. Displaced / Untagged words (often adverbs or determinants not caught)
        # We place them after subject to catch things like "emrooz" if not tagged as ADV
        if components.untagged_words:
            # Filter out the '!' if it was left over
            clean_untagged = [w for w in components.untagged_words if w != '!']
            if clean_untagged:
                parts.append(' '.join(clean_untagged).strip('.'))
        
        # 5. Object
        if flags.object_found:
            parts.append(f"{components.object} را")
        
        # 6. Complements (Prepositional Phrases)
        if flags.complement_found:
            parts.append(f"{components.adposition} {components.complement}")
        
        # 7. Verb Adverb (Manner)
        if flags.verb_adverb_found:
            parts.append(components.verb_adverb)
            
        # 8. Noun Complement (for linking verbs)
        if flags.noun_complement_found:
            parts.append(components.noun_complement)
            
        # 9. Verb
        parts.append(corrected_verb)
        
        sentence = ' '.join(parts).strip()
        
        # Punctuation
        if components.final_punctuation:
             sentence += components.final_punctuation
        else:
             sentence += '.'
        
        # Cleanup spaces
        return sentence.replace("  ", " ")
   
    def correct(self, text: str) -> str:
        """Main method to correct Persian grammar in text"""
        normalized_text = p.normalizer(text)
        tokens = p.getwordtokens(normalized_text)
        tags = p.tagger(tokens)
        
        components, flags = self._parse_sentence_components(tags)
        
        if not flags.verb_found:
            return text
        
        verb_full = components.verb
        
        #Handle compound verbs splitting for analysis/conjugation
        if '_' in verb_full:
            parts = verb_full.split('_')
            noun_part = parts[0] # e.g., 'dars' or 'doost'
            # The actual verb (e.g., 'nevesht', 'daram') is the last part
            conjugatable_part = parts[-1] 
        else:
            noun_part = ""
            conjugatable_part = verb_full
        
        # Get Lemma
        lemma_full = p.lemmatizer(conjugatable_part)
        lemma_root = lemma_full.split('#')[0]
        
        # Analyze Properties
        verb_props = self._analyze_verb_properties(
            conjugatable_part, lemma_full, flags.linking_verb, flags.verb_part_found, noun_part
        )
        
        tense = verb_props.to_tense()
        if not tense:
            return text
        
        # Clean the stem before conjugation (remove prefixes like 'mi', 'nemi')
        clean_root = lemma_root 
        if verb_props.is_present and '#' in lemma_full:
            clean_root = lemma_full.split('#')[1]
        
        # Special case: Linking verbs plural correction (Ast -> Hastand)
        if flags.linking_verb and flags.subject_is_plural and clean_root == 'است':
            clean_root = 'هست'

        # Conjugate
        verb_list = p.conjugation(clean_root, tense)

        if verb_list:
            corrected_verb_part = self._select_correct_verb_form(
                components.subject, flags.subject_is_plural, verb_list
            )
            
            # Reassemble compound verb
            # If we had a noun_part, ensure it is prepended
            if noun_part and noun_part not in corrected_verb_part:
                corrected_verb = f"{noun_part} {corrected_verb_part}"
            else:
                corrected_verb = corrected_verb_part
                
            corrected_verb = corrected_verb.replace("_", "‌")
        else:
            corrected_verb = components.verb.replace("_", "‌")
        
        starting_adverb, verb_adverb = self._classify_adverbs(components.adverbs)
        components.starting_adverb = starting_adverb
        components.verb_adverb = verb_adverb
        flags.starting_adverb_found = bool(starting_adverb)
        flags.verb_adverb_found = bool(verb_adverb)
        
        corrected_sentence = self._build_corrected_sentence(components, flags, corrected_verb)
        
        normalized_result = p.normalizer(corrected_sentence)
        return normalized_result


# Singleton instance
_grammar_checker_instance = None

def get_grammar_checker():
    global _grammar_checker_instance
    if _grammar_checker_instance is None:
        _grammar_checker_instance = PersianGrammarChecker()
    return _grammar_checker_instance

def correction(text: str) -> str:
    checker = get_grammar_checker()
    return checker.correct(text)