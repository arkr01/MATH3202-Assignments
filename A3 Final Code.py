demands = [36, 33, 33, 40, 42, 29, 33, 36, 40, 47, 31, 37, 25, 25, 33, 42, 42, 38, 29, 34, 34, 36,
           38, 47, 34, 43, 29, 22, 26, 36]

high_demands = [59, 54, 51, 60, 64, 50, 63, 56, 69, 87, 54, 66, 38, 45, 57, 69, 70, 59, 44, 63, 53,
                67, 66, 79, 64, 73, 51, 42, 41, 60]

p_high = 0.4
p_normal = 1 - p_high

p_high_reduced = 0.1
p_normal_increased = 1 - p_high_reduced

p_HH = 0.5
p_HN = 1 - p_HH

p_NH = 0.2
p_NN = 1 - p_NH

battery_cap = 80


def cost(a):
    if a == 0:
        return 0
    return 300 + battery_cap * pow(a, 0.9)


_electrigrid = {}


def electrigrid(j, s, n, was_high):
    if j == 30:
        return 0, 0, 0, None
    if (j, s, n, was_high) not in _electrigrid:
        if n == 0:
            if was_high:
                _electrigrid[j, s, n, was_high] = min(
                    (p_HH * (cost(a) + electrigrid(j + 1, min(s + a - high_demands[j],
                                                              battery_cap), n, True)[0]) +
                     p_HN * (cost(a) + electrigrid(j + 1, min(s + a - demands[j], battery_cap),
                                                   n, False)[0]), a, n)
                    for a in range(max(0, high_demands[j] - s),
                                   battery_cap - s + high_demands[j] + 1))
            else:
                _electrigrid[j, s, n, was_high] = min(
                    (p_NH * (cost(a) + electrigrid(j + 1, min(s + a - high_demands[j], battery_cap),
                                                   n, True)[0]) +
                     p_NN * (cost(a) + electrigrid(j + 1, min(s + a - demands[j], battery_cap), n,
                                                   False)[0]), a, n)
                    for a in range(max(0, high_demands[j] - s),
                                   battery_cap - s + high_demands[j] + 1))
        else:
            if was_high:
                _electrigrid[j, s, n, was_high] = \
                    min((min(p_HH * (cost(a) + electrigrid(j + 1, min(s + a - high_demands[j],
                                                                      battery_cap), n, True)[0]) +
                             p_HN * (cost(a) + electrigrid(j + 1, min(s + a - demands[j],
                                                                      battery_cap), n, False)[0]),
                             p_high_reduced * (cost(a) +
                                               electrigrid(j + 1, min(s + a - high_demands[j],
                                                               battery_cap), n - 1, True)[0]) +
                             p_normal_increased * (cost(a) +
                                                   electrigrid(j + 1,
                                                               min(s + a - demands[j], battery_cap),
                                                               n - 1, False)[0])), a, n)
                        for a in range(max(0, high_demands[j] - s), battery_cap - s +
                                       high_demands[j] + 1))
            else:
                _electrigrid[j, s, n, was_high] = min(
                    (min(p_NH * (cost(a) + electrigrid(j + 1, min(s + a - high_demands[j],
                                                                  battery_cap), n, True)[0]) +
                            p_NN * (cost(a) + electrigrid(j + 1, min(s + a - demands[j],
                                                                     battery_cap), n, False)[0]),
                            p_high_reduced * (cost(a) +
                                              electrigrid(j + 1,
                                                          min(s + a - high_demands[j], battery_cap),
                                                          n - 1, True)[0]) +
                            p_normal_increased * (cost(a) +
                                                  electrigrid(j + 1, min(s + a - demands[j],
                                                                         battery_cap),
                                                              n - 1, False)[0])), a, n)
                    for a in range(max(0, high_demands[j] - s),
                                   battery_cap - s + high_demands[j] + 1)
                )
    return _electrigrid[j, s, n, was_high]


print(electrigrid(0, 0, 5, False)[0])
