import os
import re
import codecs

def find_replace(path, find, repl, encoding="cp865"):
    "bytter -old_char med -new_char i en detd-fil"
    
    with codecs.open(path, "r", encoding=encoding) as f:
        string = f.read()

    string = re.sub(find, repl, string)

    with codecs.open(path, "w", encoding=encoding) as f:
        f.write(string)