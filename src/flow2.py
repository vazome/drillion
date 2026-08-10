if __name__ == "__main__":
    n = int(input())
    student_marks: dict[str, list[float]] = {}
    for _ in range(n):
        name, *line = input().split()
        scores = list(map(float, line))
        student_marks[name] = scores
    query_name = input()
    answer_no_count = student_marks[query_name]
    total: float = sum(answer_no_count) / len(answer_no_count)
    print(f"{total:.2f}")
