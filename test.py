from pprint import pprint

nums = [-255, 255, 129, 128, 127, -128, -129]

def s8bnumfilter(num):
    if num > 127:
        num -= 256
    if num < -128:
        num += 256
    return num

pprint(list(map(s8bnumfilter, nums)))