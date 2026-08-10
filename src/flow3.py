if __name__ == "__main__":
    a = []

    for _ in range(int(input())):
        name = input()
        score = float(input())

        x = []
        x.append(name)
        x.append(score)
        a.append(x)

    grades = []
    for i in a:
        grades.append(i[1])
    grades = list(sorted(set(grades), reverse=True))

    names = []
    for i in a:
        if i[1] == grades[-2]:
            names.append(i[0])

    names = sorted(names)
    for i in names:
        print(i)
