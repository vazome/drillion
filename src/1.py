def solution(number):
    a = []
    if number <= 0:
        return 0
    for i in range(1, number):
        if i % 3 == 0 or i % 5 == 0:
            a.append(i)
    print(sum(a))


solution(7)
