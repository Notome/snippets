def task1(arr):
    def quicksort(arr):
        if len(arr) <= 1:
            return arr
        pivot = arr[0]
        less = []
        equal = []
        more = []
        for x in arr:
            if x < pivot:
                less.append(x)
            elif x == pivot:
                equal.append(x)
            elif x > pivot:
                more.append(x)
        return quicksort(less) + equal + quicksort(more)
    return quicksort(arr)

print(task1([5, 2, 9, 1, 5]))

def task2(arr):
    return sorted(arr, key=lambda x: len(x))
print(task2(["apple", "banana", "kiwi", "pear"]))

def task3(arr):
    def digit_sum(num):
        result = 0
        for x in str(num):
            result += int(x)
        return result 
    return sorted(arr, key=lambda x: digit_sum(x))
print(task3([123, 45, 6, 789]))

def task4(arr):
    arr_set = list(set(arr))
    return sorted(arr_set, key=lambda x: arr.count(x), reverse=True)
print(task4(["apple", "banana", "apple", "cherry", "banana"]))