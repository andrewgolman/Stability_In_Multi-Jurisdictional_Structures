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

sort_ratios()