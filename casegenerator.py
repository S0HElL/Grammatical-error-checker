import itertools

flags = ["nounclauseflag", "startingadverbflag", "subjectflag", "complementflag", "object_flag",  "verbadverbflag", "nouncomplementflag", "verbflag"]

flag_mapping = {
    "nounclauseflag": "nounclause",
    "startingadverbflag": "adverb",
    "subjectflag": "subject",
    "complementflag": "complement",
    "object_flag": "object_",
    "verbadverbflag": "adverb",
    "nouncomplementflag": "nouncomplement",
    "verbflag": "verb"
}

combinations = list(itertools.product([0, 1], repeat=len(flags)))

for original_combo in combinations:
    # Applying additional constraints
    if original_combo[2] == 0 or (original_combo[4] == 1 and original_combo[6] == 1) or original_combo[-1] == 0:
        continue
    
    # Create a new variable for the modified combination
    combo = (original_combo[0], original_combo[1], 1, original_combo[3], original_combo[4], original_combo[5], original_combo[6], 1)
    
    case_statement = f"case ({', '.join(map(str, original_combo))}):"
    output_list = [f"{{{flag_mapping[flag]}}}" if value else "" for flag, value in zip(flags, original_combo) if value]
    output = f"    new_sentence = f\"{' '.join(output_list)}\""
    
    print(case_statement)
    print(output)
