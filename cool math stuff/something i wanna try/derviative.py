import tkinter as tk
from tkinter import messagebox
from sympy import symbols, diff, factorial, simplify, sympify, lambdify
import matplotlib.pyplot as plt
import numpy as np

def taylor_poly(func_str, x0, n):

    x = symbols('x')

    #try to parse the function string
    try:
        f = sympify(func_str)
    except Exception as e:
        messagebox.showerror("Invalid function", str(e))
        return None

    taylor_poly = 0

    for k in range(n + 1): #calculating the derivatives using the degree and adding them up using the Taylor formula

        deriv = diff(f, x, k)
        term = (deriv.subs(x, x0) / factorial(k)) * (x - x0)**k
        taylor_poly += term


    return simplify(taylor_poly), f


def plot_taylor(func_str, x0, n):
    """plot the given function in purple and the Taylor polynome in green"""

    result = taylor_poly(func_str, x0, n)
    if result is None:

        return

    taylor, f = result
    x = symbols('x')
    f_numeric = lambdify(x, f, 'numpy')
    taylor_numeric = lambdify(x, taylor, 'numpy')

    ###TODO: maybe adjust the space to automatically adapt to the function or hard code it?
    x_vals = np.linspace(x0- 5, x0 +5, 400) #if you increase (or decrease if you are on the negative side) the 5 the y axis gets ridiculously huge (try it!)
    try:
        y_vals = f_numeric(x_vals)
        y_taylor = taylor_numeric(x_vals)
    except Exception as e:
        messagebox.showerror("Plot error", str(e))
        return


    plt.figure(figsize=(6,6))
    plt.plot(x_vals, y_vals, label=f'f(x) = {func_str}', color='purple')
    plt.plot(x_vals, y_taylor, label=f'Taylor degree {n} @ x={x0}', color='green', linestyle='-') #purple and green cuz i love the joker 
    plt.axvline(x0, color='black', linestyle=':')
    plt.title("f(x) vs Taylor polynomial")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.grid(True)
    plt.legend()
    plt.show()


def on_submit():
    try:
        func_str = entry_func.get()
        x0 = float(entry_x0.get())
        n = int(entry_n.get())
        if n < 0:
            messagebox.showwarning("Invalid input", "Degree must be non-negative!")
            return
        
        plot_taylor(func_str, x0, n)
    except ValueError:
        messagebox.showerror("Ivalid input", "Please enter valid numbers for x0 and n.")

root = tk.Tk()
root.title("Taylor polynomial Visualizer")

tk.Label(root, text="Function f(x):").grid(row=0, column=0)

entry_func = tk.Entry(root, width= 30)
entry_func.insert(0, "sin(x)")
entry_func.grid(row=0, column=1)

tk.Label(root, text="Expansion point x₀:").grid(row=1, column=0)

entry_x0 = tk.Entry(root, width=30)
entry_x0.insert(0, "0")
entry_x0.grid(row=1, column=1)

tk.Label(root, text="Degree n:").grid(row=2, column=0)

entry_n = tk.Entry(root, width=30)
entry_n.insert(0, "5")
entry_n.grid(row=2, column=1)

tk.Button(root, text="Generate Plot", command=on_submit).grid(row=3, column=0, columnspan=2, pady=10)

root.mainloop()
