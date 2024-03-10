import sys
import os

s = sys.path[0]
p = os.path.split(s)
if p[1] == 'library':
    p = p[0]
else:
    p = s
print(p)
