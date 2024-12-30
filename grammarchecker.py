from hazm_methods import parser as p
from filehandler import *
class grammarchecker:

    def __init__(self):
        self.grammarchecker=grammarchecker


    def correction(string):
        #simple rule-based farsi grammar correction
        #objects:
      
        string=p.normalizer(string)
        tokens=p.getwordtokens(string)
        tags=p.tagger(tokens)
        #data=parser.datamaker(tokens)

        # find parts of speech
        subject = ''
        verb = ''
        object_ = ''
        complement = ''
        adp=''
        nouncomplement = ''
        nounclause = ''
        adverbs = []  # List to store adverbs
        subjectflag = 0
        subjectisplural = 0
        verbflag = 0
        nouncomplementflag = 0
        complementflag = 0
        object_flag = 0
        nounclauseflag = 0
        verbpartflag = 0
        identifier =['م','ی','ه','یم','ید','ند']
        PRO=['من','تو','او','ما','شما','آنها']
        LinkingVerbFlag = 0

        for i in range(len(tags)):
            tag = tags[i]
            next_tag = tags[i + 1] if i + 1 < len(tags) else None
            prev_tag = tags[i - 1] if i - 1 >= 0 else None
            match tag[1]:

                case 'ADP' | 'ADP,EZ':

                    if tag[0] == "را":
                        continue
                    
                    elif next_tag and next_tag[1] in ['PRON', 'NOUN', 'NOUN,EZ','DET', 'ADJ' , 'ADJ,EZ']:
                        complement = next_tag[0]
                        complementflag = 1
                        adp=tag[0]

                
                case 'PRON' | 'NOUN' | 'NOUN,EZ':

                    if complementflag and tag[0] == complement:
                        continue

                    elif next_tag and next_tag[0]  == '!':
                        nounclause = tag[0]
                        nounclauseflag = 1

                    elif next_tag and next_tag[0] == 'را':
                        object_ = tag[0] 
                        object_flag = 1

                    elif not subjectflag:
                        subject = tag[0]
                        subjectflag += 1
                        if subject.endswith("ها") or subject.endswith("های")  or (subject.endswith("ان") and p.stemmer(subject) != subject ):
                            subjectisplural = 1 
                        

                    # elif prev_tag and complementflag and prev_tag == complement:
                    #     complement = f"{adp} {complement} {tag[0]}"
    
                    # elif prev_tag and subjectflag and prev_tag[0] == subject:
                    #     subject = f"{subject} {tag[0]}"  

                case 'DET':#حرف اشاره
                    tempflag = 1 if complement == tag[0] else 0
                    if next_tag and next_tag[1] in ['PRON', 'NOUN', 'NOUN,EZ','ADJ','ADJ,EZ']:
                        temp=list(tag)
                        temp[0]=f"{tag[0]} {next_tag[0]}"       
                        tag=tuple(temp)  
                        if tempflag:
                            complement = tag[0] 

                case 'CCONJ':#حرف ربط

                    if next_tag and next_tag[1] in ['PRON', 'NOUN', 'NOUN,EZ']:
                        if subjectflag and prev_tag[0] == subject :
                            subject = f"{subject} {tag[0]} {next_tag[0]}" 
                            subjectisplural = 1

                        elif prev_tag[0] == complement:
                            complement = f"{complement} {tag[0]} {next_tag[0]}"

                        elif prev_tag[0] == object_:
                            object_ = f"{object_} {tag[0]} {next_tag[0]}"   

                case 'ADV':
                    adverb = tag[0] 
                    adverbs.append(adverb)  # Append the adverb to the list

                case 'ADJ' | 'ADJ,EZ': #صفت را با موصوف الحاق می‌کند

                    if prev_tag and prev_tag[0] == subject:
                        subject = f"{subject} {tag[0]}"

                    elif prev_tag and prev_tag == object_:
                        object_ = f"{object_} {tag[0]}"

                    elif prev_tag and prev_tag == complement:
                        complement = f"{complement} {tag[0]}"

                    else:
                        nouncomplement = tag[0]
                        nouncomplementflag = 1

                    if tag[1] in ['CCONJ'] and next_tag and next_tag[1] == 'ADJ':
                        nouncomplement = f" {nouncomplement} {tag[0]} {next_tag[0]}"
    
                case 'VERB':

                    if not verbflag:
                        verb = tag[0]
                        verbflag += 1

                        #find out if verb is of Linking type (اسنادی) 
                        with open("LinkingVerbs.txt", "r", encoding="utf-8") as f:
                            for line in f:
                                if verb in line:
                                    LinkingVerbFlag = 1
                                    break

                    if next_tag and next_tag[1] == 'VERB':
                        verb = f"{verb}_{next_tag[0]}"
                        verbpartflag = 1
                    
                    if prev_tag and verbflag and (prev_tag[1] in ['NOUN', 'NOUN,EZ']) and (prev_tag[0] not in complement) and (prev_tag[0] not in object_):
                        if LinkingVerbFlag:
                            nouncomplement = prev_tag[0]
                            nouncomplementflag = 1
                        else:
                            verb = f"{prev_tag[0]}_{verb}"
                            verbpartflag = 1



                case 'SCONJ': #Join که to the previous tag

                    if prev_tag:

                        if prev_tag[0] in subject:
                            subject = f"{subject} {tag[0]}"

                        elif prev_tag[0] in complement:
                            complement = f"{complement} {tag[0]}"
        
        #strip the verb of its identifier
        if verbpartflag:
            for item in identifier: 
                if verb.endswith(item):
                    verb = verb.replace(item,'')   

        
        #find the type of adverbs     
        startingadverbflag = 0 
        verbadverbflag = 0
        startingadverb = ''
        verbadverb = ''
        
        with open("adverbs.txt", "r", encoding="utf-8") as f:
            for adverb in adverbs:
                found_in_text_file = any(adverb in line for line in f)
                
                if found_in_text_file:
                    startingadverbflag = 1
                    startingadverb = adverb
                else:
                    verbadverb = adverb
                    verbadverbflag = 1


                f.seek(0)  # Reset file pointer to the beginning for the next adverb
        
        # Find the stem 
        stem = p.lemmatizer(verb)
        myList = stem.split('#')  # رفت # رو --> رفت , رو
        for item in myList:
            if item in verb:
                stem = item
                present = myList.index(item) # فعل مضارع است
        #set flags                                
        negative=True if verb.startswith("ن") else False
            #فعل منفی است    
        imperfective=True if verb.startswith("نمی") or verb.startswith("می") else False
              #فعل پایا است     
        subjunctive=True if verb.startswith("ب") and present else False
           #فعل التزامی هست
        future=True if verb.startswith("خواه") else False
            #فعل آینده است
        passive=True if 'شد' in verb and not LinkingVerbFlag and not future else False
            #فعل مجهول است
        precedent=True if 'بود' in verb and not LinkingVerbFlag else False
            #فعل گذشته دور است 
        progressive=True if ('داشت' or 'دار') in verb and verbpartflag else False
        
        if future:
            present = 0 

        # صرف افعال بر اساس فلگ‌هایی که تعیین کردیم 
        verblist = None
        tense = ''
        match (present,imperfective,negative,subjunctive,passive,future,precedent,progressive):
            case (0,True, True, False, False, False,False,False):
                tense = 'negative_imperfective_past'
               
            case (0,True,False,False,False,False,False,False):
                tense = 'imperfective_past'

            case (0,False,True,False,False,False,False,False):
                tense = 'negative_pefective_past'

            case (0,False,False,False,True,False,False,False):
                tense = 'passive_perfective_past'

            case (0,False,True,False,True,False,False,False):
                tense = 'negative_passive_perfective_past'

            case (0,False,False,False,False,False,False,False):
                tense = 'perfective_past'

            case (0,False,False,False,False,False,False,True):
                tense = 'progressive_past'

            case (0,False,False,False,False,False,True,False):
                tense = 'past_precedent'

            case (0,False,True,False,False,False,True,False):
                tense = 'negative_past_precedent'
            
            case (_,False,False,False,False,True,False,False):
                tense = 'perfective_future'

            case (_,False,True,False,False,True,False,False):
                tense = 'negative_perfective_future'

            case (1,True, True,False,False,False,False,False):
                tense = 'negative_imperfective_present'

            case (1,True,False,False,False,False,False,False):
                tense = 'imperfective_present'
    
            case (1,False,False,True,False,False,False,False):
                tense = 'subjunctive_perfective_present'
             
            case (1,False,False,False,True,False,False,False):
                tense = 'passive_perfective_present'

            case (1,False,True,False,True,False,False,False):
                tense = 'negative_passive_perfective_present'

            case (1,False,True,False,False,False,False,False):
                tense = 'negative_pefective_present'

            case (1,False,False,False,False,False,False,False):
                tense = 'perfective_present'

            case (1,False,False,False,False,False,False,True):
                tense = 'progressive_present'   


        # Set verblist once based on the determined tense
        verblist = p.conjugation(stem, tense)
        #find the grammatical identifiers(شناسه)
        #identifier = p.find_difference(verb, stem)

        #find and correct the grammatical errors based on the set of rules
        #check whether the verb is incorrect
        newverb=''
        for i in range(5):               

            if  subjectisplural and PRO[i] in subject and i+3 <= 5: #مثلا من و رضا بستنی خوردیم. خوردم که به علاوه 3 می‌شود خوردیم 
                newverb = verblist[i+3]
                break

            elif subject not in PRO and subjectisplural: 
                newverb = verblist[5] 
                break  # Exit the loop once a match is found
            
            elif PRO[i] in subject :
                newverb = verblist[i]
                break  # Exit the loop once a match is found
  
            elif subject not in PRO and i == 5: #subject is in singular form
                newverb = verblist[2]
                break  



        newverb = newverb.replace("_","‌")
        p.remove_repeated_substring(newverb)

        #return the corrected sentence
        #پیاده‌سازی انواع جمله در فارسی
        #با استفاده از چند فلگ تشخیص می‌دهیم که با چه جمله ای سر و کار داریم.

        match (nounclauseflag,startingadverbflag,subjectflag,object_flag,complementflag,verbadverbflag,nouncomplementflag,verbflag):
            case (0, 0, 1, 0, 0, 0, 0, 1):
                new_sentence = f"{subject} {newverb}."
            case (0, 0, 1, 0, 0, 0, 1, 1): 
                new_sentence = f"{subject} {nouncomplement} {newverb}."
            case (0, 0, 1, 0, 0, 1, 0, 1):
                new_sentence = f"{subject} {verbadverb} {newverb}."
            case (0, 0, 1, 0, 0, 1, 1, 1):
                new_sentence = f"{subject} {verbadverb} {nouncomplement} {newverb}."
            case (0, 0, 1, 0, 1, 0, 0, 1):
                new_sentence = f"{subject} {adp} {complement} {newverb}."
            case (0, 0, 1, 0, 1, 0, 1, 1):
                new_sentence = f"{subject} {adp} {complement} {nouncomplement} {newverb}."
            case (0, 0, 1, 0, 1, 1, 0, 1):
                new_sentence = f"{subject} {adp} {complement} {verbadverb} {newverb}."
            case (0, 0, 1, 0, 1, 1, 1, 1):
                new_sentence = f"{subject} {adp} {complement} {verbadverb} {nouncomplement} {newverb}."
            case (0, 0, 1, 1, 0, 0, 0, 1):
                new_sentence = f"{subject} {object_} را {newverb}."
            case (0, 0, 1, 1, 0, 1, 0, 1):
                new_sentence = f"{subject} {object_} را {verbadverb} {newverb}."
            case (0, 0, 1, 1, 1, 0, 0, 1):
                new_sentence = f"{subject} {adp} {complement} {object_} را {newverb}."
            case (0, 0, 1, 1, 1, 1, 0, 1):
                new_sentence = f"{subject} {adp} {complement} {object_} را {verbadverb} {newverb}."
            case (0, 1, 1, 0, 0, 0, 0, 1):
                new_sentence = f"{startingadverb} {subject} {newverb}."
            case (0, 1, 1, 0, 0, 0, 1, 1):
                new_sentence = f"{startingadverb} {subject} {nouncomplement} {newverb}."
            case (0, 1, 1, 0, 0, 1, 0, 1):
                new_sentence = f"{startingadverb} {subject} {verbadverb} {newverb}."
            case (0, 1, 1, 0, 0, 1, 1, 1):
                new_sentence = f"{startingadverb} {subject} {verbadverb} {nouncomplement} {newverb}."
            case (0, 1, 1, 0, 1, 0, 0, 1):
                new_sentence = f"{startingadverb} {subject} {adp} {complement} {newverb}."
            case (0, 1, 1, 0, 1, 0, 1, 1):
                new_sentence = f"{startingadverb} {subject} {adp} {complement} {nouncomplement} {newverb}."
            case (0, 1, 1, 0, 1, 1, 0, 1):
                new_sentence = f"{startingadverb} {subject} {adp} {complement} {verbadverb} {newverb}."
            case (0, 1, 1, 0, 1, 1, 1, 1):
                new_sentence = f"{startingadverb} {subject} {adp} {complement} {verbadverb} {nouncomplement} {newverb}."
            case (0, 1, 1, 1, 0, 0, 0, 1):
                new_sentence = f"{startingadverb} {subject} {object_} را {newverb}."
            case (0, 1, 1, 1, 0, 1, 0, 1):
                new_sentence = f"{startingadverb} {subject} {object_} را {verbadverb} {newverb}."
            case (0, 1, 1, 1, 1, 0, 0, 1):
                new_sentence = f"{startingadverb} {subject} {adp} {complement} {object_} را {newverb}."
            case (0, 1, 1, 1, 1, 1, 0, 1):
                new_sentence = f"{startingadverb} {subject} {adp} {complement} {object_} را {verbadverb} {newverb}."
            case (1, 0, 1, 0, 0, 0, 0, 1):
                new_sentence = f"{nounclause}! {subject} {newverb}."
            case (1, 0, 1, 0, 0, 0, 1, 1):
                new_sentence = f"{nounclause}! {subject} {nouncomplement} {newverb}."
            case (1, 0, 1, 0, 0, 1, 0, 1):
                new_sentence = f"{nounclause}! {subject} {verbadverb} {newverb}."
            case (1, 0, 1, 0, 0, 1, 1, 1):
                new_sentence = f"{nounclause}! {subject} {verbadverb} {nouncomplement} {newverb}."
            case (1, 0, 1, 0, 1, 0, 0, 1):
                new_sentence = f"{nounclause}! {subject} {adp} {complement} {newverb}."
            case (1, 0, 1, 0, 1, 0, 1, 1):
                new_sentence = f"{nounclause}! {subject} {adp} {complement} {nouncomplement} {newverb}."
            case (1, 0, 1, 0, 1, 1, 0, 1):
                new_sentence = f"{nounclause}! {subject} {adp} {complement} {verbadverb} {newverb}."
            case (1, 0, 1, 0, 1, 1, 1, 1):
                new_sentence = f"{nounclause}! {subject} {adp} {complement} {verbadverb} {nouncomplement} {newverb}."
            case (1, 0, 1, 1, 0, 0, 0, 1):
                new_sentence = f"{nounclause}! {subject} {object_} را {newverb}."
            case (1, 0, 1, 1, 0, 1, 0, 1):
                new_sentence = f"{nounclause}! {subject} {object_} را {verbadverb} {newverb}."
            case (1, 0, 1, 1, 1, 0, 0, 1):
                new_sentence = f"{nounclause}! {subject} {adp} {complement} {object_} را  {newverb}."
            case (1, 0, 1, 1, 1, 1, 0, 1):
                new_sentence = f"{nounclause}! {subject} {adp} {complement} {object_} را  {verbadverb} {newverb}."
            case (1, 1, 1, 0, 0, 0, 0, 1):
                new_sentence = f"{nounclause}! {startingadverb} {subject} {newverb}."
            case (1, 1, 1, 0, 0, 0, 1, 1):
                new_sentence = f"{nounclause}! {startingadverb} {subject} {nouncomplement} {newverb}."
            case (1, 1, 1, 0, 0, 1, 0, 1):
                new_sentence = f"{nounclause}! {startingadverb} {subject} {verbadverb} {newverb}."
            case (1, 1, 1, 0, 0, 1, 1, 1):
                new_sentence = f"{nounclause}! {startingadverb} {subject} {verbadverb} {nouncomplement} {newverb}."
            case (1, 1, 1, 0, 1, 0, 0, 1):
                new_sentence = f"{nounclause}! {startingadverb} {subject} {adp} {complement} {newverb}."
            case (1, 1, 1, 0, 1, 0, 1, 1):
                new_sentence = f"{nounclause}! {startingadverb} {subject} {adp} {complement} {nouncomplement} {newverb}."
            case (1, 1, 1, 0, 1, 1, 0, 1):
                new_sentence = f"{nounclause}! {startingadverb} {subject} {adp} {complement} {verbadverb} {newverb}."
            case (1, 1, 1, 0, 1, 1, 1, 1):
                new_sentence = f"{nounclause}! {startingadverb} {subject} {adp} {complement} {verbadverb} {nouncomplement} {newverb}."
            case (1, 1, 1, 1, 0, 0, 0, 1):
                new_sentence = f"{nounclause}! {startingadverb} {subject} {object_} را {newverb}."
            case (1, 1, 1, 1, 0, 1, 0, 1):
                new_sentence = f"{nounclause}! {startingadverb} {subject} {object_} را {verbadverb} {newverb}."
            case (1, 1, 1, 1, 1, 0, 0, 1):
                new_sentence = f"{nounclause}! {startingadverb} {subject} {adp} {complement} {object_} را {newverb}."
            case (1, 1, 1, 1, 1, 1, 0, 1):
                new_sentence = f"{nounclause}! {startingadverb} {subject} {adp} {complement} {object_} را {verbadverb} {newverb}."                

            case (_):
                new_sentence = string #fail
            
        return new_sentence.replace("  "," ")