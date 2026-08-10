import subprocess, sys

def count_parens(text):
    balance=0; in_str=False; esc=False
    opens=0; closes=0
    for c in text:
        if in_str:
            if esc: esc=False; continue
            if c=='\\': esc=True; continue
            if c=='"': in_str=False; continue
        else:
            if c=='"': in_str=True; continue
            if c=='(':
                balance+=1; opens+=1
            elif c==')':
                balance-=1; closes+=1
    return opens,closes,balance

text = open(sys.argv[1]).read()
print(sys.argv[1], count_parens(text))
