from __future__ import unicode_literals
from hazm import *
import difflib

class parser:

    #کانستراکتور
    def init(self):
        self.parser=parser


    def remove_repeated_substring(s):
        length = len(s)
        for i in range(length // 2, 0, -1):
            substring = s[-i:]
            if s[:-i].endswith(substring):
                return s[:-i]
        return s 

    def find_difference(str1, str2):
        differ = difflib.Differ()
        diff = list(differ.compare(str1, str2))
        added_part = ''.join(x[2:] for x in diff if x.startswith('+ '))
        return added_part if added_part else ''
    
    #جداسازی جملات متن
    @staticmethod
    def getsenttokens(string):
        return sent_tokenize(string)
    
    #گرفتن توکن‌های ‌جمله
    @staticmethod
    def getwordtokens(string):
        tokenizer = WordTokenizer()
        return tokenizer.tokenize(string)
    
    def join(part1,part2):
        tokenizer = WordTokenizer()
        return tokenizer.join_verb_parts([part1 , part2])

    #گرفتن توکن بعدی
    @staticmethod
    def get_next_token(input_string):
        tokens = input_string.split()  # Assuming tokens are separated by whitespaces
        for token in tokens:
            yield token

    #نرمال‌سازی جمله
    @staticmethod
    def normalizer(string):
        normalizer = Normalizer()
        return normalizer.normalize(string)
    
    #یافتن اجزای جمله
    @staticmethod
    def tagger(token):
        tagger = POSTagger(model='resources/pos_tagger.model')
        return tagger.tag(token)
    
    #یافتن مفعول و متمم در جمله بر اساس کلمات بعدی
    @staticmethod
    def datamaker(token):
          tagger = POSTagger(model='resources/pos_tagger.model')
          return tagger.data_maker(token)
        


    #یافتن بن فعل
    @staticmethod
    def lemmatizer(word):
        lemmatizer = Lemmatizer()
        if word:
            return lemmatizer.lemmatize(word)
        else:
            return ""
        
    #ریشه‌یابی کلمات
    @staticmethod
    def stemmer(string):
        stemmer = Stemmer()
        return stemmer.stem(string)
    
    #صرف فعل ها با گرفتن بن فعل و زمان آن
    @staticmethod
    def conjugation(verb,tense):
        conj = Conjugation()
        match tense:

            #صرف فعل گذشته ساده
            case "perfective_past":
                return conj.perfective_past(verb)
            
            case "negative_perfective_past":
                return conj.negative_perfective_past(verb)
            
            case "passive_perfective_past":
                return conj.passive_perfective_past(verb)
            
            case "negative_passive_perfective_past":
                return conj.negative_passive_perfective_past(verb)
            
            
            #گذشته پایا
            case "imperfective_past":
                return conj.imperfective_past(verb)
            
            case "negative_imperfective_past":
                return conj.negative_imperfective_past(verb)
            
            case "passive_imperfective_past":
                return conj.passive_imperfective_past(verb)
            
            case "negative_passive_imperfective_past":
                return conj.negative_passive_imperfective_past(verb)
            
            
            #گذشته دور
            case "past_precedent":
                return conj.past_precedent(verb)
            
            case "negative_past_precedent":
                return conj.negative_past_precedent(verb)
            
            
            #گذشته استمراری
            case "progressive_past":
                return conj.past_progresive(verb)
            
            
            #حال ساده
            case "perfective_present":
                return conj.perfective_present(verb)
            
            case "negative_perfective_present":
                return conj.negative_perfective_present(verb)
            
            case "passive_perfective_present":
                return conj.passive_perfective_present(verb)
            
            case "negative_passive_perfective_present":
                return conj.negative_passive_perfective_present(verb)
            
            #حال پایا
            case "imperfective_present":
                return conj.imperfective_present(verb)
            
            case "negative_imperfective_present":
                return conj.negative_imperfective_present(verb)
            
            case "passive_imperfective_present":
                return conj.passive_imperfective_present(verb)
            
            case "negative_passive_imperfective_present":
                return conj.negative_passive_imperfective_present(verb)
            
           #حال التزامی 
            case "subjunctive_perfective_present":
                return conj.subjunctive_perfective_present(verb)
            
            #حال استمراری
            case "progressive_present":
                return conj.present_progresive(verb)
            
            #آینده
            case "perfective_future":
                return conj.perfective_future(verb)
            case "negative_perfective_future":
                return conj.negative_perfective_future
