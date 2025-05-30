import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import json
import os
from tkcalendar import DateEntry
import datetime
import customtkinter as ctk

DATA_FILE = "tasks_data.json"

incomplete_tasks = []
completed_tasks = []

# ---------------------- Login interface ---------------------- #
def show_login_window():
    login_window = ctk.CTk()
    login_window.title("Login")
    login_window.geometry("300x180")
    login_window.resizable(False, False)

    ctk.CTkLabel(login_window, text="Alen personal task management system", font=("Segoe UI", 15, "bold")).pack(pady=(10, 0))
    ctk.CTkLabel(login_window, text="Enter Password", font=("Segoe UI", 14)).pack(pady=(10, 5))
    password_entry = ctk.CTkEntry(login_window, show="*", width=200)
    password_entry.pack(pady=5)

    def attempt_login():
        if password_entry.get() == "123456":
            login_window.destroy()
            root.deiconify()  
        else:
            messagebox.showerror("Login Failed", "Incorrect password")

    ctk.CTkButton(login_window, text="Login", command=attempt_login).pack(pady=10)
    login_window.mainloop()


# ---------------------- Data reading and writing ---------------------- #
def save_tasks():
    """Save tasks to a JSON file."""
    data = {
        "incomplete": incomplete_tasks,
        "completed": completed_tasks
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_tasks():
    """Load tasks from a JSON file."""
    global incomplete_tasks, completed_tasks
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                incomplete_tasks = data.get("incomplete", [])
                completed_tasks = data.get("completed", [])
            except:
                incomplete_tasks = []
                completed_tasks = []

# ---------------------- Interface/Treeview updates ---------------------- #
def update_incomplete_tree():
    for item in tree_incomplete.get_children():
        tree_incomplete.delete(item)

    priority_order = {"High": 0, "Medium": 1, "Low": 2}

    def sort_key(task):
        priority = priority_order.get(task.get("priority", "Medium"), 1)
        due_str = task.get("due", "")
        try:
            due_date = datetime.datetime.strptime(due_str, "%Y-%m-%d").date()
        except:
            due_date = datetime.date.max  
        return (priority, due_date)  

    sorted_tasks = sorted(incomplete_tasks, key=sort_key)

    for idx, task in enumerate(sorted_tasks, start=1):
        tree_incomplete.insert("", "end", values=(
            idx,
            task["name"],
            task["case"],
            task.get("priority", "Medium"),
            task.get("due", ""),
            task.get("note", "")
        ))


def update_completed_tree(tree_widget, count_label):
    """Rebuild the 'completed' Treeview in the completed-tasks window."""
    for item in tree_widget.get_children():
        tree_widget.delete(item)
    for idx, task in enumerate(completed_tasks, start=1):
        tree_widget.insert("", "end", values=(
            idx,
            task["name"],
            task["case"],
            task.get("status", ""),
            task.get("note", "")
        ))
    count_label.config(text=f"Completed Task Count: {len(completed_tasks)}")

# ---------------------- Deadline ---------------------- #
def check_due_dates():
    today = datetime.date.today()
    warnings = []

    for task in incomplete_tasks:
        due_str = task.get("due")
        if not due_str:
            continue
        try:
            due_date = datetime.datetime.strptime(due_str, "%Y-%m-%d").date()
            delta = (due_date - today).days
            if delta < 0:
                warnings.append(f"Overdue: {task['name']} (due {due_str})")
            elif delta <= 5:
                warnings.append(f"Due soon: {task['name']} (in {delta} day(s))")
        except:
            continue

    if warnings:
        messagebox.showinfo("Due Date Alerts", "\n".join(warnings))


# ---------------------- Search function for unfinished tasks ---------------------- #
def search_tasks():
    query = search_entry.get().strip().lower()
    if not query:
        update_incomplete_tree()  
        return
    filtered_tasks = []
    mode = search_mode.get()
    for task in incomplete_tasks:
        if mode == "name" and query in task["name"].lower():
            filtered_tasks.append(task)
        elif mode == "case" and query in task["case"].lower():
            filtered_tasks.append(task)
    tree_incomplete.delete(*tree_incomplete.get_children())
    for idx, task in enumerate(filtered_tasks, start=1):
        tree_incomplete.insert("", "end", values=(
            idx,
            task["name"],
            task["case"],
            task.get("note", "")
        ))

def reset_search():
    search_entry.delete(0, tk.END)
    update_incomplete_tree()

# ---------------------- Function ---------------------- #
def add_task():
    """Open a popup window to add a new task."""
    add_window = tk.Toplevel(root)
    add_window.title("Add Task")
    add_window.geometry("350x300")
  
    frm = ttk.Frame(add_window, padding=10)
    frm.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(frm, text="Name:").grid(row=0, column=0, sticky="e", pady=5)
    name_entry = ctk.CTkEntry(frm, width=200)
    name_entry.grid(row=0, column=1, pady=5)

    ttk.Label(frm, text="Case/Task:").grid(row=1, column=0, sticky="e", pady=5)
    case_entry = ctk.CTkEntry(frm, width=200)
    case_entry.grid(row=1, column=1, pady=5)

    ttk.Label(frm, text="Note:").grid(row=2, column=0, sticky="e", pady=5)
    note_entry = ctk.CTkEntry(frm, width=200)
    note_entry.grid(row=2, column=1, pady=5)

    ttk.Label(frm, text="Status:").grid(row=3, column=0, sticky="e", pady=5)
    status = tk.StringVar(value="Incomplete")
    rb_frame = ttk.Frame(frm)
    rb_frame.grid(row=3, column=1, pady=5, sticky="w")
    ttk.Radiobutton(rb_frame, text="Incomplete", variable=status, value="Incomplete").pack(side=tk.LEFT)
    ttk.Radiobutton(rb_frame, text="Complete", variable=status, value="Complete").pack(side=tk.LEFT)

    ttk.Label(frm, text="Priority:").grid(row=4, column=0, sticky="e", pady=5)
    priority_var = tk.StringVar(value="Medium")
    priority_combo = ttk.Combobox(frm, textvariable=priority_var, values=["High", "Medium", "Low"], state="readonly", width=27)
    priority_combo.grid(row=4, column=1, pady=5)

    ttk.Label(frm, text="Due Date:").grid(row=5, column=0, sticky="e", pady=5)
    due_date_picker = DateEntry(frm, width=27, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
    due_date_picker.grid(row=5, column=1, pady=5)
    
    def save_new_task():
        name = name_entry.get().strip()
        case = case_entry.get().strip()
        note = note_entry.get().strip()
        priority = priority_var.get()
        due_date = due_date_picker.get()
        task_status = status.get()
        if not name or not case:
            messagebox.showwarning("Input Error", "Please fill in all fields", parent=add_window)
            return
        task = {"name": name, "case": case, "note": note, "status": task_status, "priority": priority, "due": due_date}
        
        if task_status == "Complete":
            task["status"] = "Lodged"
            completed_tasks.append(task)
        else:
            incomplete_tasks.append(task)
            update_incomplete_tree()
        save_tasks()
        add_window.destroy()
    
    btn_save = ctk.CTkButton(frm, text="Save", command=save_new_task)
    btn_save.grid(row=6, column=1, sticky="e", pady=10)

def mark_as_complete():
    selected_item = tree_incomplete.focus()
    if not selected_item:
        messagebox.showwarning("Selection Error", "Please select a task to mark as complete")
        return

    selected_values = tree_incomplete.item(selected_item, "values")
    selected_name = selected_values[1]
    selected_case = selected_values[2]
    selected_priority = selected_values[3]
    selected_due = selected_values[4]
    selected_note = selected_values[5]

    index_in_list = -1
    for i, task in enumerate(incomplete_tasks):
        if (task.get("name") == selected_name and
            task.get("case") == selected_case and
            task.get("priority") == selected_priority and
            (task.get("due") or "") == selected_due and
            task.get("note") == selected_note):
            index_in_list = i
            break

    if index_in_list == -1:
        messagebox.showerror("Error", "Task not found in list")
        return

    task = incomplete_tasks.pop(index_in_list)
    task["status"] = "Lodged"
    completed_tasks.append(task)
    update_incomplete_tree()
    save_tasks()


def delete_incomplete_task():
    selected_item = tree_incomplete.focus()
    if not selected_item:
        messagebox.showwarning("Selection Error", "Please select a task to delete")
        return

    selected_values = tree_incomplete.item(selected_item, "values")
    selected_name = selected_values[1]
    selected_case = selected_values[2]
    selected_priority = selected_values[3]
    selected_due = selected_values[4]
    selected_note = selected_values[5]

    index_in_list = -1
    for i, task in enumerate(incomplete_tasks):
        if (task.get("name") == selected_name and
            task.get("case") == selected_case and
            task.get("priority") == selected_priority and
            (task.get("due") or "") == selected_due and
            task.get("note") == selected_note):
            index_in_list = i
            break

    if index_in_list == -1:
        messagebox.showerror("Error", "Task not found in list")
        return

    incomplete_tasks.pop(index_in_list)
    update_incomplete_tree()
    save_tasks()


def edit_note():
    """Edit the 'Note', 'Priority', and 'Due Date' of a selected incomplete task."""
    selected_item = tree_incomplete.focus()
    if not selected_item:
        messagebox.showwarning("Selection Error", "Please select a task to edit", parent=root)
        return

    selected_values = tree_incomplete.item(selected_item, "values")
    selected_name = selected_values[1]
    selected_case = selected_values[2]
    selected_priority = selected_values[3]
    selected_due = selected_values[4]
    selected_note = selected_values[5]

    index_in_list = -1
    for i, task in enumerate(incomplete_tasks):
        if (task.get("name") == selected_name and
            task.get("case") == selected_case and
            task.get("priority") == selected_priority and
            (task.get("due") or "") == selected_due and
            task.get("note") == selected_note):
            index_in_list = i
            break

    if index_in_list == -1:
        messagebox.showerror("Error", "Task not found in original list", parent=root)
        return

    original_task = incomplete_tasks[index_in_list]
    task_copy = original_task.copy()

    edit_window = tk.Toplevel(root)
    edit_window.title("Edit Task")
    edit_window.geometry("400x250")

    frm = ttk.Frame(edit_window, padding=10)
    frm.pack(fill=tk.BOTH, expand=True)

    # Note
    ttk.Label(frm, text="Note:").grid(row=0, column=0, sticky="e", pady=5)
    note_entry = ctk.CTkEntry(frm, width=200)
    note_entry.insert(0, task_copy.get("note", ""))
    note_entry.grid(row=0, column=1, pady=5)

    # Priority
    ttk.Label(frm, text="Priority:").grid(row=1, column=0, sticky="e", pady=5)
    priority_var = tk.StringVar()
    priority_var.set(task_copy.get("priority", "Medium"))
    priority_combo = ttk.Combobox(frm, textvariable=priority_var, values=["High", "Medium", "Low"], state="readonly", width=37)
    priority_combo.grid(row=1, column=1, pady=5)

    # Enable Due Date checkbox
    ttk.Label(frm, text="Enable Due Date:").grid(row=2, column=0, sticky="e", pady=5)
    use_due_var = tk.BooleanVar(value=bool(task_copy.get("due")))
    chk_use_due = ttk.Checkbutton(frm, variable=use_due_var, command=lambda: toggle_due_state())
    chk_use_due.grid(row=2, column=1, sticky="w", pady=5)

    # Due Date
    ttk.Label(frm, text="Due Date:").grid(row=3, column=0, sticky="e", pady=5)
    due_entry = DateEntry(frm, width=37, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
    try:
        due_default = datetime.datetime.strptime(task_copy.get("due", ""), "%Y-%m-%d").date()
    except:
        due_default = datetime.date.today()
    due_entry.set_date(due_default)
    due_entry.grid(row=3, column=1, pady=5)

    def toggle_due_state():
        if use_due_var.get():
            due_entry.config(state="normal")
        else:
            due_entry.config(state="disabled")

    toggle_due_state()

    def save_note_priority_due():
        updated_task = incomplete_tasks[index_in_list]
        updated_task["note"] = note_entry.get().strip()
        updated_task["priority"] = priority_var.get()
        if use_due_var.get():
            updated_task["due"] = due_entry.get()
        else:
            updated_task["due"] = ""
        update_incomplete_tree()
        save_tasks()
        edit_window.destroy()

    btn_save = ctk.CTkButton(frm, text="Save Changes", command=save_note_priority_due)
    btn_save.grid(row=4, column=1, sticky="e", pady=10)

# ---------------------- 已完成任务窗口 ---------------------- #
def show_completed_tasks():

    global comp_window, tree_completed, lbl_count
    comp_window = tk.Toplevel(root)
    comp_window.title("Completed Tasks")
    comp_window.geometry("850x600")
    
    frm = ttk.Frame(comp_window, padding=10)
    frm.pack(fill=tk.BOTH, expand=True)
    
    search_frame_comp = ttk.Frame(frm)
    search_frame_comp.pack(fill=tk.X, pady=5)
    
    ttk.Label(search_frame_comp, text="Search:").pack(side=tk.LEFT, padx=5)
    comp_search_entry = ctk.CTkEntry(search_frame_comp, width=20)
    comp_search_entry.pack(side=tk.LEFT, padx=5)
    
    ttk.Label(search_frame_comp, text="Search by:").pack(side=tk.LEFT, padx=5)
    comp_search_mode = tk.StringVar(value="name")
    rbtn_name_comp = ttk.Radiobutton(search_frame_comp, text="Name", variable=comp_search_mode, value="name")
    rbtn_name_comp.pack(side=tk.LEFT, padx=5)
    rbtn_case_comp = ttk.Radiobutton(search_frame_comp, text="Case", variable=comp_search_mode, value="case")
    rbtn_case_comp.pack(side=tk.LEFT, padx=5)
    rbtn_case_comp = ttk.Radiobutton(search_frame_comp, text="Status", variable=comp_search_mode, value="status")
    rbtn_case_comp.pack(side=tk.LEFT, padx=5)

    def search_completed_tasks():
        query = comp_search_entry.get().strip().lower()
        if not query:
            update_completed_tree(tree_completed, lbl_count)
            return
        filtered = []
        mode = comp_search_mode.get()
        for task in completed_tasks:
            if mode == "name" and query in task.get("name", "").lower():
                filtered.append(task)
            elif mode == "case" and query in task.get("case", "").lower():
                filtered.append(task)
            elif mode == "status" and query in task.get("status", "").lower():
                filtered.append(task)
        tree_completed.delete(*tree_completed.get_children())
        for idx, task in enumerate(filtered, start=1):
            tree_completed.insert("", "end", values=(idx, task.get("name", ""), task.get("case", ""), task.get("status", "")))
        lbl_count.config(text=f"Completed Task Count: {len(filtered)}")
    
    def reset_completed_search():
        comp_search_entry.delete(0, tk.END)
        update_completed_tree(tree_completed, lbl_count)
    
    btn_search_comp = ctk.CTkButton(search_frame_comp, text="Search", command=search_completed_tasks)
    btn_search_comp.pack(side=tk.LEFT, padx=5)
    btn_reset_comp = ctk.CTkButton(search_frame_comp, text="Reset", command=reset_completed_search)
    btn_reset_comp.pack(side=tk.LEFT, padx=5)
    
    lbl_count = ttk.Label(frm, text=f"Completed Task Count: {len(completed_tasks)}", 
                          font=("Segoe UI", 12, "bold"))
    lbl_count.pack(pady=5)
    
    container_comp = ttk.Frame(frm)
    container_comp.pack(fill=tk.BOTH, expand=True)

    columns_comp = ("Index", "Name", "Case", "Status", "Note")
    tree_completed = ttk.Treeview(container_comp, columns=columns_comp, show="headings", height=10)
    tree_completed.grid(row=0, column=0, sticky="nsew")
    
    tree_completed.heading("Index", text="#")
    tree_completed.heading("Name", text="Name")
    tree_completed.heading("Case", text="Case/Task")
    tree_completed.heading("Status", text="Status")
    
    tree_completed.column("Index", width=40, anchor="center")
    tree_completed.column("Name", width=150, anchor="center")
    tree_completed.column("Case", width=200, anchor="w")
    tree_completed.column("Status", width=100, anchor="center")
    tree_completed.heading("Note", text="Note")
    tree_completed.column("Note", width=400, anchor="w")

    scrollbar_comp = ttk.Scrollbar(container_comp, orient="vertical", command=tree_completed.yview)
    scrollbar_comp.grid(row=0, column=1, sticky="ns")
    tree_completed.configure(yscrollcommand=scrollbar_comp.set)
    
    hscrollbar_comp = ttk.Scrollbar(container_comp, orient="horizontal", command=tree_completed.xview)
    hscrollbar_comp.grid(row=1, column=0, sticky="ew")
    tree_completed.configure(xscrollcommand=hscrollbar_comp.set)
    
    container_comp.rowconfigure(0, weight=1)
    container_comp.columnconfigure(0, weight=1)
    
    update_completed_tree(tree_completed, lbl_count)
    btn_frame_comp = ttk.Frame(frm)
    btn_frame_comp.pack(pady=5, anchor="w")

    btn_delete = ctk.CTkButton(btn_frame_comp, text="Delete Selected Task", command=delete_completed_task)
    btn_delete.pack(side=tk.LEFT, padx=10)

    btn_edit = ctk.CTkButton(btn_frame_comp, text="Modify Selected Task", command=edit_completed_task)
    btn_edit.pack(side=tk.LEFT, padx=10)

    btn_restore = ctk.CTkButton(btn_frame_comp, text="Move Back to Incomplete", command=move_back_to_incomplete)
    btn_restore.pack(side=tk.LEFT, padx=10)

    
def delete_completed_task():
    selected_item = tree_completed.focus()
    if not selected_item:
        messagebox.showwarning("Selection Error", "Please select a task to delete", parent=comp_window)
        return
    index_in_tree = tree_completed.index(selected_item)
    if index_in_tree < 0 or index_in_tree >= len(completed_tasks):
        return
    completed_tasks.pop(index_in_tree)
    update_completed_tree(tree_completed, lbl_count)
    save_tasks()


def edit_completed_task():
    selected_item = tree_completed.focus()
    if not selected_item:
        messagebox.showwarning("Selection Error", "Please select a task to modify", parent=comp_window)
        return

    selected_values = tree_completed.item(selected_item, "values")
    selected_name = selected_values[1]
    selected_case = selected_values[2]
    selected_status = selected_values[3]
    selected_note = selected_values[4]

    index_in_list = next(
        (i for i, t in enumerate(completed_tasks)
         if (t.get("name") or "") == selected_name and
            (t.get("case") or "") == selected_case and
            (t.get("status") or "") == selected_status and
            (t.get("note") or "") == selected_note),
        -1
    )

    if index_in_list == -1:
        messagebox.showerror("Error", "Task not found in data list", parent=comp_window)
        return

    task = completed_tasks[index_in_list]

    edit_window = tk.Toplevel(comp_window)
    edit_window.title("Edit Completed Task")
    edit_window.geometry("400x250")

    frm_edit = ttk.Frame(edit_window, padding=10)
    frm_edit.pack(fill=tk.BOTH, expand=True)

    ttk.Label(frm_edit, text="Name:").grid(row=0, column=0, sticky="e", pady=5)
    name_entry = ctk.CTkEntry(frm_edit, width=200)
    name_entry.insert(0, task.get("name", ""))
    name_entry.grid(row=0, column=1, pady=5)

    ttk.Label(frm_edit, text="Case/Task:").grid(row=1, column=0, sticky="e", pady=5)
    case_entry = ctk.CTkEntry(frm_edit, width=200)
    case_entry.insert(0, task.get("case", ""))
    case_entry.grid(row=1, column=1, pady=5)

    ttk.Label(frm_edit, text="Note:").grid(row=2, column=0, sticky="e", pady=5)
    note_entry = ctk.CTkEntry(frm_edit, width=200)
    note_entry.insert(0, task.get("note", ""))
    note_entry.grid(row=2, column=1, pady=5)

    ttk.Label(frm_edit, text="Status:").grid(row=3, column=0, sticky="e", pady=5)
    status_values = ("Lodged", "Completed", "Granted", "Refused")
    status_var = tk.StringVar()
    status_var.set(task.get("status", "Lodged"))
    status_combobox = ttk.Combobox(frm_edit, textvariable=status_var, values=status_values, state="readonly", width=33)
    status_combobox.grid(row=3, column=1, pady=5)

    def save_edit():
        new_name = name_entry.get().strip()
        new_case = case_entry.get().strip()
        new_note = note_entry.get().strip()
        new_status = status_var.get()
        if not new_name or not new_case:
            messagebox.showwarning("Input Error", "Please fill in all fields", parent=edit_window)
            return
        task["name"] = new_name
        task["case"] = new_case
        task["note"] = new_note
        task["status"] = new_status
        update_completed_tree(tree_completed, lbl_count)
        save_tasks()
        edit_window.destroy()

    btn_save_edit = ttk.Button(frm_edit, text="Save Changes", command=save_edit)
    btn_save_edit.grid(row=4, column=1, sticky="e", pady=10)

def move_back_to_incomplete():
    selected_item = tree_completed.focus()
    if not selected_item:
        messagebox.showwarning("Selection Error", "Please select a task to move back", parent=comp_window)
        return

    selected_values = tree_completed.item(selected_item, "values")
    selected_name = selected_values[1]
    selected_case = selected_values[2]
    selected_status = selected_values[3]
    selected_note = selected_values[4]

    index_in_list = next(
        (i for i, t in enumerate(completed_tasks)
         if (t.get("name") or "") == selected_name and
            (t.get("case") or "") == selected_case and
            (t.get("status") or "") == selected_status and
            (t.get("note") or "") == selected_note),
        -1
    )

    if index_in_list == -1:
        messagebox.showerror("Error", "Task not found in completed list", parent=comp_window)
        return

    original_task = completed_tasks.pop(index_in_list)

    clean_task = {
        "name": original_task.get("name", ""),
        "case": original_task.get("case", ""),
        "note": original_task.get("note", ""),
        "priority": original_task.get("priority", "Medium"),
        "due": original_task.get("due", "")
    }

    incomplete_tasks.append(clean_task)
    update_completed_tree(tree_completed, lbl_count)
    update_incomplete_tree()
    save_tasks()
    messagebox.showinfo("Success", f"Task '{clean_task['name']}' moved back to Incomplete", parent=comp_window)

# ---------------------- Main window interface ---------------------- #
ctk.set_appearance_mode("Light")  
ctk.set_default_color_theme("blue") 

root = ctk.CTk()
root.title("Task Recorder - Created by Alen")
root.geometry("930x640")
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview",
                background="white",
                foreground="black",
                fieldbackground="white",
                rowheight=30,
                font=("Segoe UI", 11))
style.configure("Treeview.Heading",
                background="#ececec",
                foreground="black",
                font=("Segoe UI", 11, "bold"))
style.map("Treeview", background=[("selected", "#a3d2ff")])

main_frame = ctk.CTkFrame(root, fg_color="#1e1e1e", corner_radius=15)
main_frame.pack(fill=tk.BOTH, expand=True)

lf_incomplete = ttk.LabelFrame(
    main_frame,
    text="Incomplete Tasks",
    labelanchor="n",  
    padding=10
)

style = ttk.Style()
style.configure("TLabelframe.Label", font=("Segoe UI", 14, "bold"))

lf_incomplete.pack(fill=tk.BOTH, expand=True, side=tk.TOP)

# ---------------------- Search function area for unfinished tasks ---------------------- #
search_frame = ctk.CTkFrame(lf_incomplete, fg_color="transparent")
search_frame.pack(fill=tk.X, pady=5)

ctk.CTkLabel(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
search_entry = ctk.CTkEntry(search_frame, width=200)
search_entry.pack(side=tk.LEFT, padx=5)

ctk.CTkLabel(search_frame, text="Search by:").pack(side=tk.LEFT, padx=5)
search_mode = tk.StringVar(value="name")
rbtn_name = ctk.CTkRadioButton(search_frame, text="Name", variable=search_mode, value="name")
rbtn_name.pack(side=tk.LEFT, padx=5)

rbtn_case = ctk.CTkRadioButton(search_frame, text="Case", variable=search_mode, value="case")
rbtn_case.pack(side=tk.LEFT, padx=5)


btn_search = ctk.CTkButton(search_frame, text="Search", command=search_tasks)
btn_search.pack(side=tk.LEFT, padx=5)
btn_reset = ctk.CTkButton(search_frame, text="Reset", command=reset_search)
btn_reset.pack(side=tk.LEFT, padx=5)

# ---------------------- Treeview and scroll bar area of ​​the unfinished task area ---------------------- #
container = ttk.Frame(lf_incomplete)
container.pack(fill=tk.BOTH, expand=True)

columns = ("Index", "Name", "Case", "Priority", "Due", "Note")
tree_incomplete = ttk.Treeview(container, columns=columns, show="headings", height=10)
tree_incomplete.grid(row=0, column=0, sticky="nsew")

tree_incomplete.heading("Index", text="#")
tree_incomplete.heading("Name", text="Name")
tree_incomplete.heading("Case", text="Case/Task")
tree_incomplete.heading("Priority", text="Priority")
tree_incomplete.heading("Due", text="Due Date")
tree_incomplete.heading("Note", text="Note")

tree_incomplete.column("Index", width=40, anchor="center", stretch=False)
tree_incomplete.column("Name", width=150, anchor="center", stretch=False)
tree_incomplete.column("Case", width=150, anchor="w", stretch=False)
tree_incomplete.column("Note", width=600, anchor="w", stretch=False)
tree_incomplete.column("Priority", width=80, anchor="center", stretch=False)
tree_incomplete.column("Due", width=100, anchor="center", stretch=False)

scrollbar_main = ttk.Scrollbar(container, orient="vertical", command=tree_incomplete.yview)
scrollbar_main.grid(row=0, column=1, sticky="ns")
tree_incomplete.configure(yscrollcommand=scrollbar_main.set)

hscrollbar_main = ttk.Scrollbar(container, orient="horizontal", command=tree_incomplete.xview)
hscrollbar_main.grid(row=1, column=0, sticky="ew")
tree_incomplete.configure(xscrollcommand=hscrollbar_main.set)

container.rowconfigure(0, weight=1)
container.columnconfigure(0, weight=1)

# ---------------------- Transfer task ---------------------- #

def transfer_selected_task():
    selected_item = tree_incomplete.focus()
    if not selected_item:
        messagebox.showwarning("Error", "Please select a task first")
        return

    index_in_tree = tree_incomplete.index(selected_item)
    if index_in_tree < 0 or index_in_tree >= len(incomplete_tasks):
        return

    task = incomplete_tasks[index_in_tree]

    transfer_window = tk.Toplevel(root)
    transfer_window.title("Transfer Task")
    transfer_window.geometry("300x150")

    ttk.Label(transfer_window, text="Send to:").pack(pady=10)

    colleagues = {
        "Josh": "192.168.1.33",
        "Alen": "192.168.1.35",
    }

    name_var = tk.StringVar()
    name_menu = ttk.Combobox(transfer_window, textvariable=name_var, values=list(colleagues.keys()), state="readonly")
    name_menu.pack(pady=5)

    def confirm_transfer():
        name = name_var.get()
        if name not in colleagues:
            messagebox.showwarning("Error", "Please select a valid recipient", parent=transfer_window)
            return
        ip = colleagues[name]
        try:
            import requests
            url = f"http://{ip}:6789/send-task"
            res = requests.post(url, json=task)
            if res.status_code == 200:
                messagebox.showinfo("Successful", f"Transferred to {name}", parent=transfer_window)
                task["status"] = f"Transferred to {name}"
                completed_tasks.append(task)
                incomplete_tasks.pop(index_in_tree)
                update_incomplete_tree()
                save_tasks()
                transfer_window.destroy()
            else:
                messagebox.showwarning("Error", f"Transfer failed: {res.text}", parent=transfer_window)
        except Exception as e:
            messagebox.showerror("Network Error", f"Unable to connect {name}：{e}", parent=transfer_window)

    ctk.CTkButton(transfer_window, text="Confirm transfer", command=confirm_transfer).pack(pady=10)

# ---------------------- LOCKING ---------------------- #
def lock_screen():
    global root
    root.withdraw()  
    show_login_window() 

# ---------------------- Load received file ---------------------- #
def load_received_tasks():
    try:
        received = []
        with open("received_tasks.json", "r", encoding="utf-8") as f:
            for line in f:
                task = json.loads(line.strip())
                task["note"] = task.get("note", "") + " (received)"
                received.append(task)

        incomplete_tasks.extend(received)

        save_tasks()

        open("received_tasks.json", "w", encoding="utf-8").close()

    except FileNotFoundError:
        pass

# ---------------------- Bottom button area ---------------------- #
btn_frame = ttk.Frame(main_frame, padding=10)
btn_frame.pack(fill=tk.X, expand=False, side=tk.BOTTOM)

btn_row1 = ttk.Frame(btn_frame)
btn_row1.pack(pady=5)

btn_add = ctk.CTkButton(btn_row1, text="Add Task", command=add_task, width=150)
btn_add.pack(side=tk.LEFT, padx=10)

btn_mark = ctk.CTkButton(btn_row1, text="Mark as Complete", command=mark_as_complete, width=150)
btn_mark.pack(side=tk.LEFT, padx=10)

btn_delete_incomplete = ctk.CTkButton(btn_row1, text="Delete Task", command=delete_incomplete_task, width=150)
btn_delete_incomplete.pack(side=tk.LEFT, padx=10)

btn_show = ctk.CTkButton(btn_row1, text="Show Completed Tasks", command=show_completed_tasks, width=180)
btn_show.pack(side=tk.LEFT, padx=10)

btn_row2 = ttk.Frame(btn_frame)
btn_row2.pack(pady=5)

btn_edit_note = ctk.CTkButton(btn_row2, text="Edit Note", command=edit_note, width=150)
btn_edit_note.pack(side=tk.LEFT, padx=10)

btn_transfer = ctk.CTkButton(btn_row2, text="Transfer This Task", command=transfer_selected_task, width=180)
btn_transfer.pack(side=tk.LEFT, padx=10)

btn_lock = ctk.CTkButton(btn_row2, text="Lock", command=lock_screen, width=100)
btn_lock.pack(side=tk.LEFT, padx=10)



# ---------------------- Start loading data ---------------------- #
def main_app():
    load_tasks()
    load_received_tasks()
    update_incomplete_tree()
    check_due_dates()
    root.withdraw()   
    show_login_window()  
    root.mainloop()   

main_app()


