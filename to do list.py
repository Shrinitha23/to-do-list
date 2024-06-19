import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime

# Database setup
conn = sqlite3.connect('todo_list.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                priority INTEGER NOT NULL,
                due_date TEXT,
                category TEXT,
                completed INTEGER NOT NULL)''')
conn.commit()

class ToDoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List Application")

        self.task_var = tk.StringVar()
        self.priority_var = tk.IntVar()
        self.due_date_var = tk.StringVar()
        self.category_var = tk.StringVar()

        self.create_widgets()
        self.display_tasks()

    def create_widgets(self):
        # Entry fields for task, priority, due date, and category
        tk.Label(self.root, text="Task:").grid(row=0, column=0)
        tk.Entry(self.root, textvariable=self.task_var).grid(row=0, column=1)

        tk.Label(self.root, text="Priority (1-5):").grid(row=1, column=0)
        tk.Entry(self.root, textvariable=self.priority_var).grid(row=1, column=1)

        tk.Label(self.root, text="Due Date (YYYY-MM-DD):").grid(row=2, column=0)
        tk.Entry(self.root, textvariable=self.due_date_var).grid(row=2, column=1)

        tk.Label(self.root, text="Category:").grid(row=3, column=0)
        tk.Entry(self.root, textvariable=self.category_var).grid(row=3, column=1)

        # Buttons to add, update, and delete tasks
        tk.Button(self.root, text="Add Task", command=self.add_task).grid(row=4, column=0, columnspan=2)
        tk.Button(self.root, text="Update Task", command=self.update_task).grid(row=5, column=0, columnspan=2)
        tk.Button(self.root, text="Delete Task", command=self.delete_task).grid(row=6, column=0, columnspan=2)
        tk.Button(self.root, text="Mark as Complete", command=self.complete_task).grid(row=7, column=0, columnspan=2)

        # Listbox to display tasks
        self.task_listbox = tk.Listbox(self.root, selectmode=tk.SINGLE)
        self.task_listbox.grid(row=8, column=0, columnspan=2, pady=10)
        self.task_listbox.bind('<<ListboxSelect>>', self.load_task)

    def add_task(self):
        task = self.task_var.get()
        priority = self.priority_var.get()
        due_date = self.due_date_var.get()
        category = self.category_var.get()

        if not task or not priority or not due_date:
            messagebox.showwarning("Input Error", "Task, Priority, and Due Date are required fields.")
            return

        try:
            datetime.strptime(due_date, '%Y-%m-%d')
        except ValueError:
            messagebox.showwarning("Input Error", "Due Date must be in YYYY-MM-DD format.")
            return

        c.execute('''INSERT INTO tasks (task, priority, due_date, category, completed)
                     VALUES (?, ?, ?, ?, ?)''', (task, priority, due_date, category, 0))
        conn.commit()
        self.display_tasks()

    def update_task(self):
        selected_task = self.task_listbox.curselection()
        if not selected_task:
            messagebox.showwarning("Selection Error", "No task selected.")
            return

        task_id = self.task_listbox.get(selected_task).split()[0]
        task = self.task_var.get()
        priority = self.priority_var.get()
        due_date = self.due_date_var.get()
        category = self.category_var.get()

        if not task or not priority or not due_date:
            messagebox.showwarning("Input Error", "Task, Priority, and Due Date are required fields.")
            return

        try:
            datetime.strptime(due_date, '%Y-%m-%d')
        except ValueError:
            messagebox.showwarning("Input Error", "Due Date must be in YYYY-MM-DD format.")
            return

        c.execute('''UPDATE tasks SET task=?, priority=?, due_date=?, category=? WHERE id=?''',
                  (task, priority, due_date, category, task_id))
        conn.commit()
        self.display_tasks()

    def delete_task(self):
        selected_task = self.task_listbox.curselection()
        if not selected_task:
            messagebox.showwarning("Selection Error", "No task selected.")
            return

        task_id = self.task_listbox.get(selected_task).split()[0]
        c.execute('DELETE FROM tasks WHERE id=?', (task_id,))
        conn.commit()
        self.display_tasks()

    def complete_task(self):
        selected_task = self.task_listbox.curselection()
        if not selected_task:
            messagebox.showwarning("Selection Error", "No task selected.")
            return

        task_id = self.task_listbox.get(selected_task).split()[0]
        c.execute('UPDATE tasks SET completed=? WHERE id=?', (1, task_id))
        conn.commit()
        self.display_tasks()

    def display_tasks(self):
        self.task_listbox.delete(0, tk.END)
        for row in c.execute('SELECT * FROM tasks ORDER BY due_date'):
            task_str = f"{row[0]} {row[1]} - Priority: {row[2]}, Due: {row[3]}, Category: {row[4]}, {'Completed' if row[5] else 'Incomplete'}"
            self.task_listbox.insert(tk.END, task_str)

    def load_task(self, event):
        selected_task = self.task_listbox.curselection()
        if not selected_task:
            return

        task_id = self.task_listbox.get(selected_task).split()[0]
        task = c.execute('SELECT * FROM tasks WHERE id=?', (task_id,)).fetchone()

        self.task_var.set(task[1])
        self.priority_var.set(task[2])
        self.due_date_var.set(task[3])
        self.category_var.set(task[4])

if __name__ == "__main__":
    root = tk.Tk()
    app = ToDoApp(root)
    root.mainloop()

    # Close the database connection when the application is closed
    conn.close()
