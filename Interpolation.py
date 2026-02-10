# Author: Marco Wiens
# Version:09.04.2024
# interpolations
# different functions for interpolation


def intpol(xb, Points, xx, yy):
    x = []
    y = []
    yb = -99999

    xx = [float(val) for val in xx]
    yy = [float(val) for val in yy]

    for i in range(Points):
        x.append(xx[i])
        y.append(yy[i])

    for i in range(len(x) - 1):
        xmarker = (x[i] - xb) * (x[i + 1] - xb)
        if xmarker <= 0:
            yb = y[i] + (xb - x[i]) / (x[i + 1] - x[i]) * (y[i + 1] - y[i])
            break

    return yb

def intp_new(bereich, n, XN, YN, x):
    SPAN = XN[n-1] - XN[0]
    y = 0
    L = 1
    NM = n

    GoOn = 1

    if bereich == 1:
        if n < 4:
            GoOn = 0
        else:
            NM = 4
    elif bereich == 2:
        GoOn = 0

    if GoOn == 1:
        while not ((SPAN > 0 and x < XN[L]) or (SPAN < 0 and x > XN[L])) and GoOn == 1:
            if L == n:
                L = n - 3
                GoOn = 0 
            L += 1

    if GoOn == 1:
        if L > 2:
            if L != n:
                L -= 2
            else:
                L = n - 3
        else:
            L = 1

    for L1 in range(1, NM + 1):
        CO = 1
        for L2 in range(1, NM + 1):
            if L1 == L2:
                TEMP = 1
            else:
                TEMP = (x - XN[L + L2 - 2]) / (XN[L + L1 - 2] - XN[L + L2 - 2])
            CO *= TEMP
        y += CO * YN[L + L1 - 2]

    return y
