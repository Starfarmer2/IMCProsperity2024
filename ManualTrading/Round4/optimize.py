# def my_function(variables):
#     L, H = variables
#     p1 = 50*(H**2) + L*(H**2)/2 - (L**3)/2 - (H**3)/2
#     return -p1
def my_function(variables):
    L, H = variables
    p1 = (L**2/2 - 900*L + 405000) * (1000-L)
    p2 = (H**2/2-900*H-L**2/2+900*L)*(1000-H)
    return -p1-p2

initial_guess = [933, 955]

from scipy.optimize import minimize

result = minimize(my_function, initial_guess, method='BFGS')
print("Optimal parameters:", result.x)
print("Minimum value:", result.fun)
