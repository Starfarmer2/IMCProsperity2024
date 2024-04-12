
def find_profit(L: int,H: int, k: float=1) -> float:
    p1 = k/100*(1000-L)*(L-900)
    p2 = k/100*(H-L)*(1000-H)
    return p1+p2

#Case 933, 966
print(find_profit(920,967))

