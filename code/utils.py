def costs(size, pos, med=0):
    return 1. / size + abs(pos - med)


def absolute_cost_reduction(old_costs, new_costs):
    return old_costs - new_costs


def relative_cost_reduction(old_costs, new_costs):
    return 1 - new_costs / old_costs


def sort_ratios(in_file="2coalitionsDIV.txt", out_file="2DIVratio.txt"):
    file = open(in_file, "r")
    out = open(out_file, "w")
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


def get_pairs(in_file="results/2DIVratio.txt"):
    file = open(in_file, "r")
    pairs = []
    for i in file:
        items = i.split(" ")
        pairs.append((int(items[2].strip()), int(items[3].strip())))
    return pairs


def get_data(in_file="results/2coalitionsDATA.txt"):
    """return format: (L R dist EPS)"""
    file = open(in_file, "r")
    data = []
    for i in file:
        items = i.split(" ")
        items = list(map(lambda x: float(x.strip()), items))
        data.append(items)
    return data


def non_negative(f):
    def func(*args, **kwargs):
        return max(0, f(*args, **kwargs))
    return func
