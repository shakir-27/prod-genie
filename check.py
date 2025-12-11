def process_data(items):
    result = []
    for item in items:
        if item > 0:
            result.append(item * 2)
        else:
            result.append(item)
    return result

def main():
    data = [1, 2, 3, 4, 5]
    output = process_data(data)
    print(output)

if __name__ == "__main__":
    main()





def calculate(a, b, c):
    x = a + b
    y = x * c
    z = y - a
    return z

def transform(l):
    r = []
    for i in l:
        if i % 2 == 0:
            r.append(i ** 2)
        else:
            r.append(i + 1)
    return r

def compute(n):
    s = 0
    for i in range(n):
        s += i
    return s

def filter_values(v):
    output_list = []
    for x in v:
        if x > 10:
            o.append(x)
    return o

