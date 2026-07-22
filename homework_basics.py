def get_length(s: str) -> int:
    return len(s)
result1 = get_length('hello world')
print(result1)
def concat_string(s1: str, s2: str) -> str:
    return s1+s2
result2=concat_string('hello','world')
print(result2)
def get_square(n:float) -> float:
    return n**2
result3=get_square(3.7)
print(result3)
def get_sum(n1:float, n2:float) -> float:
    return n1 + n2
result4=get_sum(3.6,4.2)
print(result4)
def div_reminder(n1:int, n2:int) -> tuple:
    return n1//n2, n1%n2
result5=div_reminder(14,3)
print(result5)
def get_average(list1:list) -> float:
    return sum(list1)/len(list1)
result6=get_average([1,2,3,4,5])
print(result6)
def common_elements(list1:list, list2:list) -> list:
    return list(set(list1).intersection(list2))
result7=common_elements([1,2,3,4,5],[4,5,6,7,8])
print(result7)
def get_dict_keys(d:dict):
    for key in d.keys():
        print(key)
get_dict_keys({'a': 1, 'b': 2, 'c': 3})
def get_dict_sum(d1:dict, d2:dict) -> dict:
    merged= d1.copy()
    merged.update(d2)
    return merged
result9=get_dict_sum({'a':1,'b':2,'c':3},{'a':4,'b':5,'c':6})
print(result9)
def get_sets_union(set1:set, set2:set) -> set:
    return set1.union(set2)
result10=get_sets_union({1,2,3},{4,5,6})
print(result10)
def is_subset(s1: set, s2: set) -> bool:
    return s1.issubset(s2)
result11 = is_subset({1, 2}, {1, 2, 3, 4})
print( result11)
def check_par(n: int):
    if n % 2 == 0:
        print(f"Число {n} — Парне")
    else:
        print(f"Число {n} — Непарне")
check_par(10)
check_par(9)
def filter_even_num(lst: list) -> list:
    return [x for x in lst if x % 2 == 0]
result12 = filter_even_num([1, 2, 3, 4, 5, 6, 7, 8])
print(result12)
check_even_lambda = lambda n: "парне" if n % 2 == 0 else "не парне"
print(check_even_lambda(14))
print(check_even_lambda(15))




