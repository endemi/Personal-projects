def is_even(num):
    return num % 2 == 0

#input, Expected Output, actual output

#33, False, False
print(is_even(33))

#0, False, True
print(is_even(0))

#77, False, False
print(is_even(77))

#-87, False, False
print(is_even(-87))

#-52, True, True
print(is_even(-52))