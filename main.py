import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import datetime
import matplotlib.pyplot as plt

# ---------------- DATABASE ----------------
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",   # 🔴 CHANGE
    database="finance_db"
)
cursor = conn.cursor()

# ---------------- FUNCTIONS ----------------
def add_data():
    try:
        t_type = type_var.get()
        amount = float(amount_entry.get())
        category = category_entry.get()
        date = str(datetime.date.today())

        if t_type == "" or category == "":
            messagebox.showerror("Error", "All fields required!")
            return

        cursor.execute(
            "INSERT INTO transactions (type, amount, category, date) VALUES (%s,%s,%s,%s)",
            (t_type, amount, category, date)
        )
        conn.commit()

        show_data()
        clear_fields()

    except:
        messagebox.showerror("Error", "Invalid input")

def show_data():
    for row in tree.get_children():
        tree.delete(row)

    cursor.execute("SELECT * FROM transactions")
    for row in cursor.fetchall():
        tree.insert("", "end", values=row[1:])

def delete_data():
    selected = tree.selection()
    if not selected:
        messagebox.showerror("Error", "Select record")
        return

    values = tree.item(selected)["values"]

    cursor.execute(
        "DELETE FROM transactions WHERE type=%s AND amount=%s AND category=%s AND date=%s",
        (values[0], values[1], values[2], values[3])
    )
    conn.commit()

    show_data()

def load_selected(event):
    selected = tree.selection()
    if selected:
        values = tree.item(selected)["values"]

        type_var.set(values[0])
        amount_entry.delete(0, tk.END)
        amount_entry.insert(0, values[1])
        category_entry.delete(0, tk.END)
        category_entry.insert(0, values[2])

def update_data():
    selected = tree.selection()

    if not selected:
        messagebox.showerror("Error", "Select record")
        return

    old = tree.item(selected)["values"]

    cursor.execute("""
    UPDATE transactions 
    SET type=%s, amount=%s, category=%s
    WHERE type=%s AND amount=%s AND category=%s AND date=%s
    """, (type_var.get(), float(amount_entry.get()), category_entry.get(),
          old[0], old[1], old[2], old[3]))

    conn.commit()
    show_data()
    clear_fields()

def clear_fields():
    type_var.set("")
    amount_entry.delete(0, tk.END)
    category_entry.delete(0, tk.END)

def show_bar_chart():
    cursor.execute("SELECT * FROM transactions")
    data = cursor.fetchall()

    income, expense = 0, 0

    for row in data:
        if row[1] == "Income":
            income += row[2]
        else:
            expense += row[2]

    plt.figure()
    plt.bar(["Income", "Expense"], [income, expense])
    plt.title("Income vs Expense")
    plt.show()

def show_pie_chart():
    cursor.execute("""
    SELECT category, SUM(amount)
    FROM transactions
    WHERE type='Expense'
    GROUP BY category
    """)
    data = cursor.fetchall()

    if not data:
        messagebox.showinfo("Info", "No data")
        return

    labels = [x[0] for x in data]
    values = [x[1] for x in data]

    plt.figure()
    plt.pie(values, labels=labels, autopct='%1.1f%%')
    plt.title("Expense Distribution")
    plt.show()

# ---------------- UI ----------------
root = tk.Tk()
root.title("Finance Tracker Pro 💰")
root.geometry("950x600")
root.configure(bg="#121212")

# -------- Sidebar --------
sidebar = tk.Frame(root, bg="#1f1f2e", width=200)
sidebar.pack(side="left", fill="y")

tk.Label(sidebar, text="💰 Finance App",
         bg="#1f1f2e", fg="white",
         font=("Arial", 14, "bold")).pack(pady=20)

def menu_btn(text):
    return tk.Button(sidebar, text=text,
                     bg="#2c2c3c", fg="white",
                     relief="flat", width=20, height=2)

menu_btn("Dashboard").pack(pady=5)
menu_btn("Transactions").pack(pady=5)
menu_btn("Reports").pack(pady=5)

# -------- Main Area --------
main = tk.Frame(root, bg="#121212")
main.pack(side="right", fill="both", expand=True)

tk.Label(main, text="Dashboard",
         bg="#121212", fg="white",
         font=("Arial", 20, "bold")).pack(pady=10)

# -------- Form --------
form = tk.Frame(main, bg="#1e1e2f")
form.pack(pady=10)

label_style = {"bg": "#1e1e2f", "fg": "white"}

tk.Label(form, text="Type", **label_style).grid(row=0, column=0, padx=10, pady=5)
tk.Label(form, text="Amount", **label_style).grid(row=1, column=0, padx=10, pady=5)
tk.Label(form, text="Category", **label_style).grid(row=2, column=0, padx=10, pady=5)

type_var = ttk.Combobox(form, values=["Income", "Expense"])
type_var.grid(row=0, column=1)

amount_entry = tk.Entry(form)
amount_entry.grid(row=1, column=1)

category_entry = tk.Entry(form)
category_entry.grid(row=2, column=1)

# -------- Buttons --------
btn_frame = tk.Frame(main, bg="#121212")
btn_frame.pack(pady=10)

def btn(text, cmd, color):
    return tk.Button(btn_frame, text=text, command=cmd,
                     bg=color, fg="white",
                     width=15, height=2)

btn("Add", add_data, "#4CAF50").grid(row=0, column=0, padx=10)
btn("Update", update_data, "#2196F3").grid(row=0, column=1, padx=10)
btn("Delete", delete_data, "#f44336").grid(row=0, column=2, padx=10)

btn("Bar Chart", show_bar_chart, "#9C27B0").grid(row=1, column=0, pady=5)
btn("Pie Chart", show_pie_chart, "#FF9800").grid(row=1, column=1, pady=5)

# -------- Table --------
table_frame = tk.Frame(main)
table_frame.pack(fill="both", expand=True, padx=20, pady=20)

style = ttk.Style()
style.configure("Treeview",
                background="#2c2c3c",
                foreground="white",
                rowheight=25,
                fieldbackground="#2c2c3c")

tree = ttk.Treeview(table_frame,
                    columns=("Type","Amount","Category","Date"),
                    show="headings")

for col in ("Type","Amount","Category","Date"):
    tree.heading(col, text=col)
    tree.column(col, anchor="center")

tree.pack(fill="both", expand=True)

tree.bind("<ButtonRelease-1>", load_selected)

show_data()

root.mainloop()
