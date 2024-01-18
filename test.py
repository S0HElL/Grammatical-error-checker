from NLP_methods import parser as p
import difflib

class grammarchecker:

    def __init__(self):
        self.grammarchecker=grammarchecker

    def find_difference(str1, str2):
        differ = difflib.Differ()
        diff = list(differ.compare(str1, str2))
        added_part = ''.join(x[2:] for x in diff if x.startswith('+ '))
        return added_part

    def correction(string):
        #simple rule-based farsi grammar correction

        #objects:
        PRO=['من','تو','او','ما','شما','آنها']
        #string=p.normalizer(string)
        tokens=p.getwordtokens(string)
        tags=p.tagger(tokens)
        return tags

        # Find the verb and subject
        subject=''
        verb=''
        for tag in tags:
            if tag[1]=='VERB':
                verb = tag[0]
            elif tag[1]=='PRON' or 'NOUN' or 'NOUN,EZ':
                subject = tag[0]
                break
        
        #find the stem     
        stem=p.lemmatizer(verb)
        myList=stem.split('#') # رفت # رو --> رفت , رو
        temp = 0
        tense = ''
        for item in myList:
            if item in verb:
                stem=item
                if temp == 0:
                    tense = 'past'
                    verblist=p.conjugation(stem,tense)
                elif temp == 1:
                    tense = 'present'
                    verblist=p.conjugation(stem,tense)
            else:
                temp+=1
        
        #find the grammatical identifiers(شناسه)
        ID = grammarchecker.find_difference(verb, stem)

        #find and correct the grammatical errors based on the set of rules
        correctedverb=''
        for i in range(5):
            if subject == PRO[i]:
                correctedverb = verblist[i]
                break  # Exit the loop once a match is found
            elif subject not in PRO and ('ها' in subject or 'ان' in subject):
                correctedverb = verblist[5]
                break  # Exit the loop once a match is found
            elif subject not in PRO:
                correctedverb = verblist[2]
                break  # Exit the loop once a match is found

        #return the corrected sentence
        outputstr = ''
        token_generator = p.get_next_token(string)

        for _ in range(len(tokens)):
            next_token = next(token_generator, None)
 
            if next_token is not None and next_token == verb+'.':
                outputstr += correctedverb
            elif next_token is None:
                outputstr += '.'
                break  # Exit the loop when there are no more tokens
            else:
                 outputstr += next_token + ' '

        return outputstr
            
#driver code
print (grammarchecker.correction("ساقی نمی‌ریخت"))      
      


        
   
            


            
                