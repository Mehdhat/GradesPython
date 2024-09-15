import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector


# Function to connect to the MySQL database
def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",  # Replace with your MySQL username
            password="",  # Replace with your MySQL password
            database="student_db"  # Replace with your MySQL database name
        )
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS grades (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            student_name VARCHAR(255) NOT NULL,
                            subject VARCHAR(255) NOT NULL,
                            grade FLOAT NOT NULL)''')
        connection.commit()
        return connection
    except mysql.connector.Error as err:
        messagebox.showerror("Connection Error", f"Error: {err}")
        return None


# Function to insert data into the database
def insert_data():
    student_name = entry_student_name.get()
    subject = entry_subject.get()
    grade = entry_grade.get()

    if student_name and subject and grade:
        try:
            grade = float(grade)  # Grade must be numeric
        except ValueError:
            messagebox.showerror("Input Error", "Grade must be a numeric value.")
            return

        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute("INSERT INTO grades (student_name, subject, grade) VALUES (%s, %s, %s)",
                               (student_name, subject, grade))
                connection.commit()
                messagebox.showinfo("Success", "Data inserted successfully!")
                clear_fields()
                fetch_data()  # Refresh Treeview
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Failed to insert data: {err}")
            finally:
                cursor.close()
                connection.close()
        else:
            messagebox.showerror("Connection Error", "Failed to connect to the database.")
    else:
        messagebox.showwarning("Input Error", "All fields are required!")


# Function to fetch data from the database
def fetch_data():
    connection = connect_to_database()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT * FROM grades")
            rows = cursor.fetchall()

            # Clear previous data in the tree
            tree.delete(*tree.get_children())

            if rows:  # Check if rows is not empty
                for row in rows:
                    tree.insert("", tk.END, values=row)
            else:
                messagebox.showinfo("No Data", "No records found.")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error fetching data: {err}")
        finally:
            cursor.close()
            connection.close()


# Function to edit selected grade
def edit_grade():
    selected_item = tree.selection()
    if selected_item:
        item = tree.item(selected_item)
        values = item['values']

        # Fill the entry fields with the selected item's data
        entry_student_name.delete(0, tk.END)
        entry_student_name.insert(0, values[1])
        entry_subject.delete(0, tk.END)
        entry_subject.insert(0, values[2])
        entry_grade.delete(0, tk.END)
        entry_grade.insert(0, values[3])

        # Update the button to save changes
        submit_button.config(command=lambda: update_grade(values[0]))  # Pass the ID to update

    else:
        messagebox.showwarning("Selection Error", "Please select a record to edit.")


# Function to update the grade in the database
def update_grade(grade_id):
    student_name = entry_student_name.get()
    subject = entry_subject.get()
    grade = entry_grade.get()

    if student_name and subject and grade:
        try:
            grade = float(grade)  # Grade must be numeric
        except ValueError:
            messagebox.showerror("Input Error", "Grade must be a numeric value.")
            return

        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute("UPDATE grades SET student_name=%s, subject=%s, grade=%s WHERE id=%s",
                               (student_name, subject, grade, grade_id))
                connection.commit()
                messagebox.showinfo("Success", "Data updated successfully!")
                clear_fields()
                fetch_data()  # Refresh Treeview
                submit_button.config(command=insert_data)  # Reset the button to insert data
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Failed to update data: {err}")
            finally:
                cursor.close()
                connection.close()
        else:
            messagebox.showerror("Connection Error", "Failed to connect to the database.")
    else:
        messagebox.showwarning("Input Error", "All fields are required!")


# Function to clear input fields
def clear_fields():
    entry_student_name.delete(0, tk.END)
    entry_subject.delete(0, tk.END)
    entry_grade.delete(0, tk.END)


# Create the main window
root = tk.Tk()
root.title("Student Grades Management")
root.geometry("600x500")
root.configure(bg="#f0f0f0")

# Set the icon for the window
root.iconbitmap(r'C:\Users\Admin\Downloads\pythonProject1\127.ico')  # Update this path to your .ico file

# Create a frame for the form
frame = tk.Frame(root, bg="#ffffff", padx=20, pady=20)
frame.pack(pady=20)

# Create labels and entry fields
tk.Label(frame, text="Student Name:", bg="#ffffff", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=5)
entry_student_name = tk.Entry(frame, font=("Arial", 12))
entry_student_name.grid(row=0, column=1, padx=10, pady=5)

tk.Label(frame, text="Subject:", bg="#ffffff", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=5)
entry_subject = tk.Entry(frame, font=("Arial", 12))
entry_subject.grid(row=1, column=1, padx=10, pady=5)

tk.Label(frame, text="Grade:", bg="#ffffff", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=5)
entry_grade = tk.Entry(frame, font=("Arial", 12))
entry_grade.grid(row=2, column=1, padx=10, pady=5)

# Create a submit button
submit_button = tk.Button(frame, text="Submit", command=insert_data, bg="#44c4a1", fg="#ffffff", font=("Arial", 12),
                          padx=10, pady=5)
submit_button.grid(row=3, column=0, pady=10)

# Create a clear button
clear_button = tk.Button(frame, text="Clear", command=clear_fields, bg="#44c4a1", fg="#ffffff", font=("Arial", 12),
                         padx=10, pady=5)
clear_button.grid(row=3, column=1, pady=10)

# Create an "Edit Grade" button to fetch and display all records
edit_button = tk.Button(frame, text="Edit Grade", command=edit_grade, bg="#44c4a1", fg="#ffffff", font=("Arial", 12),
                        padx=10, pady=5)
edit_button.grid(row=4, column=0, columnspan=2, pady=10)

# Create a frame for the treeview
tree_frame = tk.Frame(root)
tree_frame.pack(pady=20)

# Create the Treeview widget
tree = ttk.Treeview(tree_frame, columns=("ID", "Student Name", "Subject", "Grade"), show='headings', height=8)
tree.heading("ID", text="ID")
tree.heading("Student Name", text="Student Name")
tree.heading("Subject", text="Subject")
tree.heading("Grade", text="Grade")
tree.column("ID", anchor=tk.CENTER, width=50)
tree.column("Student Name", anchor=tk.CENTER, width=150)
tree.column("Subject", anchor=tk.CENTER, width=150)
tree.column("Grade", anchor=tk.CENTER, width=100)
tree.pack()

# Fetch data from the database and populate the treeview when the app starts
fetch_data()

# Start the main loop
root.mainloop()

