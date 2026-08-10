l = "2 3 6 6 5"
arr = map(int, l.split())  # promise to apply function, empties after single use.
# [arr] promise wrapped into a list
# [*arr] does the below list() logic.
list_var = sorted(
    set(arr)
)  # list function that will execute the function int for each str object inside the map

print(list_var[-2])
