import json




def repeat(text, variable_name):

    [A, B] = text.split("-- TEMPLATE --")
    A = A.strip()
    B = B.strip()
    text = B
    values = list(map(lambda x: x.strip(),A.splitlines()))
    statements=[]

    for value in values:
        templated=text.replace(variable_name,value)

        statements.append(templated)


    return "\n\n".join(statements)


handler_manifest = {
    "repeat":repeat
}