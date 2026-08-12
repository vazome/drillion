# def alphabet_position(text):
text = "abcdefghijklmnopqrstuvwxyz"
print(text.index("c"))

d = "d"
print(ord(d) - ord("a") + 1)

print(chr(ord(d)))


def alphabet_position(text: str):
    controlstr = "abcdefghijklmnopqrstuvwxyz"
    text = text.lower()
    result = []
    for i in text:
        if i in controlstr:
            result.append(str(controlstr.index(i) + 1))
    line = " ".join(result)
    print(line)


alphabet_position("The sunset sets at twelve o' clock.")
