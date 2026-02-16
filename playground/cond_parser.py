import re
from geety import Component


VAR_PATTERN = re.compile(r'\$([\w\.]+)')


def cond_exec(condition, context, components=None, prevs=None):
    new_context = {}
    for var in VAR_PATTERN.findall(condition):
        if var not in context:
            return False
        if issubclass(type(context[var]), Component):
            new_context[var] = context[var].render(components, context, prevs)
        elif issubclass(type(context[var]), str):
            new_context[var] = '\'' + context[var] + '\''
        else:
            new_context[var] = context[var]
    condition = VAR_PATTERN.sub(lambda m: str({
        key: val
        for key, val in new_context.items()
    }.get(m.group(1), m.group(0))), condition)
    return eval(condition)
    
    


if __name__ == '__main__':
    cond = '$user == "mrybs" or $age >= 18'
    cond = "$test == 'mrybs'"
    conts = [
        {
            'user': 'mrybs',
            'age': 10
        },
        {
            'user': 'mrybs',
            'age': 18
        },
        {
            'user': '001kpp',
            'age': 16
        },
        {
            'user': 'well_welg',
            'age': 19
        },
        {
            'user': 'loh'
        },
        {'users': ['mrybs', '001kpp', 'test'], 'a': 1, 'b': '1', 'c': 'lolkek', 'user': 'mrybs', 'test': 'mrybs', 'class': 'Card'}
    ]
    print(cond)
    for cont in conts:
        print(cond_exec(cond, cont), cont)
    


