def sort_ratios():
    file = open("2coalitionsDIV.txt", "r")
    out = open("2DIVratio.txt", "w")
    res = []
    for s in file.readlines():
        res.append(s.split(" "))
    for i in res:
        i[0] = int(i[0])
        i[1] = int(i[1])
        i[3] = float(i[3].strip())
    res.sort(key=lambda x: -x[3])
    for i in res:
        print(round(i[3], 4), i[1]/i[0], i[1], i[0], file=out)

# sort_ratios()

def get_pairs():
    file = open("results/2DIVratio.txt", "r")
    pairs = []
    for i in file:
        items = i.split(" ")
        pairs.append((int(items[2].strip()), int(items[3].strip())))
    return pairs


def get_data():
    file = open("results/2coalitionsDATA.txt", "r")
    data = []
    for i in file:
        items = i.split(" ")
        items = list(map(lambda x: float(x.strip()), items))
        data.append(items)
    # L R dist EPS
    return data

