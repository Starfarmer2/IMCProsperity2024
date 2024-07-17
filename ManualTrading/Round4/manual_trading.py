
def find_profit(L: int,H: int, k: float=1) -> float:
    amt1 = cdf(900,L)
    p1 = amt1 * (1000 - L)

    amt2 = cdf(L, H)
    p2 = amt2 * (1000 - H)
    print(f'amt1: {amt1}, amt2: {amt2}')
    return p1+p2

def cdf(x1: int, x2: int) -> float:
    return (x2**2/2-900*x2)/5000 - (x1**2/2-900*x1)/5000



#Case 933, 966
print(find_profit(957,985))

# def lin(x):
#     return x**2/2-900*x

# print(lin(900))

