# FileHandlerModule.py
#توابع باز کردن و بستن فایل در این ماژول تعریف شده‌اند

def open_file(file_path, mode='r'):

    try:
        file_object = open(file_path, mode,encoding="utf-8")
        print(f"File '{file_path}' opened successfully.")
        return file_object
    except Exception as e:
        print(f"Error opening file '{file_path}': {e}")
        return None

def close_file(file_object):
 
    try:
        file_object.close()
        print("File closed successfully.")
    except Exception as e:
        print(f"Error closing file: {e}")

