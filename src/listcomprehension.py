from typing import Any

x = 1
y = 1
z = 1
n = 2

a: list[Any] = []
for i in range(x + 1):
    for j in range(y + 1):
        for k in range(z + 1):
            if n != sum([i, j, k]):
                a.append([i, j, k])
print(a)

# or

b: list[list[int]] = [
    [i, j, k]
    for i in range(x + 1)
    for j in range(y + 1)
    for k in range(z + 1)
    if n != sum([i, j, k])
]

print(b)
