from filehandler import open_file, close_file
from grammarchecker import grammarchecker as gc
from NLP_methods import parser as p


#تصحیح‌کننده غلط ‌های دستوری مبتنی بر قانون برای زبان فارسی
#با استفاده از کتابخانه حظم 
#سهیل تقوی - دانشگاه صنعتی شاهرود 
#پاییز 1402

#objects
file = open_file("sample_text.txt", "r")
text = file.readlines()

# generating the final output
if text:
    with open("app_log.txt", "a", encoding="utf-8") as f:
        for line in text:
            corrected_line = gc.correction(line.strip())
            f.write("Corrected: {" + corrected_line + "}\nOriginal: {" + line.strip() + "}\n")
            
            
            

#بستن فایل           
close_file(file)



