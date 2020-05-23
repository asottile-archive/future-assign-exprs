import re

from future_assign_exprs import ASSIGN
from future_assign_exprs import future_assign_exprs

reg = re.compile('<[a-z]+>')

@future_assign_exprs
def g(s):
    if ASSIGN('match', reg.match(s)):
        print(match.group())
    else:
        print('no match!')


g('wat')
g('<hi> there')
