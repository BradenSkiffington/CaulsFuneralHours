import os
import tkinter as tk
from tkinter import simpledialog, messagebox
from tkinter import ttk
from tkcalendar import Calendar
from PIL import Image, ImageTk
import subprocess

class TimesheetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Timesheet App - Cauls Funeral Home")
        self.root.geometry("1100x600")

        self.logo_frame = tk.Frame(self.root, width=400, height=600, bg='#2E4053')
        self.logo_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.create_logo()

        self.options_frame = tk.Frame(self.root, width=700, height=600, bg='#34495E')
        self.options_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.create_main_menu()

    def create_logo(self):
        self.logo_frame.pack_propagate(False)
        try:
            logo_image = Image.open("cauls.jpg")
            logo_image = logo_image.resize((400, 600), Image.ANTIALIAS)
            logo_photo = ImageTk.PhotoImage(logo_image)
            self.logo_label = tk.Label(self.logo_frame, image=logo_photo, bg='#2E4053')
            self.logo_label.image = logo_photo
            self.logo_label.pack()
        except Exception as e:
            print(f"Error loading logo: {e}")

    def create_main_menu(self):
        for widget in self.options_frame.winfo_children():
            widget.destroy()

        main_menu = tk.Frame(self.options_frame, bg='#34495E')
        main_menu.pack(pady=50)

        style = ttk.Style()
        style.configure("TButton", font=("Arial", 12), padding=10, background='#1ABC9C', foreground='#000000')
        style.map("TButton",
                  foreground=[('pressed', '#000000'), ('active', '#000000')],
                  background=[('pressed', '#16A085'), ('active', '#1ABC9C')])

        new_doc_btn = ttk.Button(main_menu, text="Create New Document", command=self.create_new_document, style="TButton")
        new_doc_btn.grid(row=0, column=0, padx=10, pady=10)

        edit_doc_btn = ttk.Button(main_menu, text="Edit Existing Document", command=self.edit_existing_document, style="TButton")
        edit_doc_btn.grid(row=1, column=0, padx=10, pady=10)

    def create_new_document(self):
        self.clear_logo_frame()

        create_doc_frame = tk.Frame(self.logo_frame, bg='#2E4053')
        create_doc_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(create_doc_frame, text="Enter the document name (without extension):", bg='#2E4053', fg='#ECF0F1', font=("Arial", 12)).pack(pady=10)
        doc_name_entry = tk.Entry(create_doc_frame, font=("Arial", 12))
        doc_name_entry.pack(pady=5)

        def save_new_document():
            name = doc_name_entry.get()
            if not name:
                messagebox.showerror("Error", "Document name cannot be empty.")
                return

            filename = f"{name}.txt"
            if os.path.exists(filename):
                messagebox.showerror("Error", "Document already exists. Try a different name.")
            else:
                with open(filename, 'w') as file:
                    header = f"{name} Hours - Cauls Funeral Home\n".center(83)
                    divider = '-' * 83 + "\n"
                    subheader = f"{'Date (MM-DD-YYYY)':<20}{'Time Range':<18}{'Hours Worked':<20}" \
                                f"{'Nights On Call':<15}{'Trips Made':<14}\n"
                    file.write(divider)
                    file.write(header)
                    file.write(divider)
                    file.write(subheader)
                    file.write(divider)
                messagebox.showinfo("Success", f"Document {filename} created successfully.")
                self.show_document_editor(filename)

        save_btn = ttk.Button(create_doc_frame, text="Save Document", command=save_new_document, style="TButton")
        save_btn.pack(pady=20)

    def clear_logo_frame(self):
        for widget in self.logo_frame.winfo_children():
            widget.destroy()

    def list_documents(self):
        files = [f for f in os.listdir() if f.endswith('.txt')]
        if not files:
            messagebox.showinfo("Info", "No documents found.")
            return []
        return files

    def edit_existing_document(self):
        files = self.list_documents()
        if not files:
            return

        file_choice = simpledialog.askstring("Choose File",
                                             "Enter the number of the document you want to edit:\n" + "\n".join(
                                                 [f"{idx + 1}. {file}" for idx, file in enumerate(files)]))
        if file_choice and file_choice.isdigit() and 1 <= int(file_choice) <= len(files):
            self.show_document_editor(files[int(file_choice) - 1])
        else:
            messagebox.showerror("Error", "Invalid choice.")
            self.edit_existing_document()

    def show_document_editor(self, filename):
        self.clear_logo_frame()

        # Add a canvas for scrolling
        canvas = tk.Canvas(self.logo_frame, bg='#5D6D7E')  # Update the background color
        scrollbar = ttk.Scrollbar(self.logo_frame, orient="vertical", command=canvas.yview)

        style = ttk.Style()
        style.configure("TFrame", background='#5D6D7E', padding=(5, 5, 5, 5))  # Update the background color

        scrollable_frame = ttk.Frame(canvas, style='TFrame')  # Use the style

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tk.Label(scrollable_frame, text=f"Editing document: {filename}", font=("Arial", 14), background='#5D6D7E', foreground='#ECF0F1').pack(pady=10)

        header_frame = tk.Frame(scrollable_frame, bg='#5D6D7E')
        header_frame.pack()

        headers = ["Date (MM-DD-YYYY)", "Time Range", "Hours Worked", "Nights On Call", "Trips Made"]
        for header in headers:
            lbl = tk.Label(header_frame, text=header, font=("Arial", 12, "bold"), padx=10, pady=5, borderwidth=1, relief="solid", background='#34495E', foreground='#ECF0F1')
            lbl.pack(side=tk.LEFT)

        entries_frame = tk.Frame(scrollable_frame, bg='#5D6D7E')
        entries_frame.pack(pady=5, fill=tk.X)

        with open(filename, 'r') as file:
            lines = file.readlines()[4:]  # Skip the header lines and divider
            for line_idx, line in enumerate(lines):
                if line.startswith("Total"):
                    break  # Stop reading when we reach totals
                data = line.strip().split()
                if len(data) < 5:
                    continue  # Skip incomplete or malformed lines

                # Create a frame for each time entry
                time_entry_frame = tk.Frame(entries_frame, bg='#5D6D7E')
                time_entry_frame.pack(pady=5, fill=tk.X)

                # Display the time entry
                for idx, entry in enumerate(data):
                    entry_label = tk.Label(time_entry_frame, text=f"{entry:<20}", padx=10, pady=5, borderwidth=1, relief="solid", background='#34495E', foreground='#ECF0F1')
                    entry_label.pack(side=tk.LEFT)

                # Button to remove this time entry
                remove_btn = ttk.Button(time_entry_frame, text="Remove", command=lambda line_idx=line_idx: self.remove_time_entry(filename, line_idx), style="TButton")
                remove_btn.pack(side=tk.RIGHT, padx=10)

        add_entry_btn = ttk.Button(scrollable_frame, text="Add Time Entry", command=lambda: self.add_time_entry(filename), style="TButton")
        add_entry_btn.pack(pady=10)

        open_btn = ttk.Button(scrollable_frame, text="Open Document", command=lambda: self.open_document(filename), style="TButton")
        open_btn.pack(pady=10)

        # Place the back button on the right side
        back_btn = ttk.Button(scrollable_frame, text="Back to Main Menu", command=self.create_main_menu, style="TButton")
        back_btn.pack(pady=20, anchor='e')

        # Update totals in the document
        self.update_document_totals(filename)

    def add_time_entry(self, filename):
        entry_frame = tk.Frame(self.logo_frame, bg='#2E4053')
        entry_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(entry_frame, text="Enter the date (MM-DD-YYYY):", bg='#2E4053', fg='#ECF0F1', font=("Arial", 12)).pack(pady=5)
        cal = Calendar(entry_frame, selectmode='day', date_pattern='mm-dd-yyyy', background='#2E4053', foreground='#ECF0F1', headersbackground='#1ABC9C', normalbackground='#34495E', weekendbackground='#34495E', othermonthbackground='#2E4053', othermonthwebackground='#2E4053', selectbackground='#1ABC9C', selectforeground='#ECF0F1')
        cal.pack(pady=5)

        tk.Label(entry_frame, text="Enter time range:", bg='#2E4053', fg='#ECF0F1', font=("Arial", 12)).pack(pady=5)
        time_range_entry = tk.Entry(entry_frame, font=("Arial", 12))
        time_range_entry.pack(pady=5)

        tk.Label(entry_frame, text="Enter hours worked:", bg='#2E4053', fg='#ECF0F1', font=("Arial", 12)).pack(pady=5)
        hours_entry = tk.Entry(entry_frame, font=("Arial", 12))
        hours_entry.pack(pady=5)

        tk.Label(entry_frame, text="Enter nights on call (0 or 1):", bg='#2E4053', fg='#ECF0F1', font=("Arial", 12)).pack(pady=5)
        nights_entry = tk.Entry(entry_frame, font=("Arial", 12))
        nights_entry.pack(pady=5)

        tk.Label(entry_frame, text="Enter trips made:", bg='#2E4053', fg='#ECF0F1', font=("Arial", 12)).pack(pady=5)
        trips_entry = tk.Entry(entry_frame, font=("Arial", 12))
        trips_entry.pack(pady=5)

        def save_entry():
            date = cal.get_date()
            time_range = time_range_entry.get()
            hours_worked = hours_entry.get()
            nights_on_call = nights_entry.get()
            trips_made = trips_entry.get()

            try:
                hours_worked = float(hours_worked)
                nights_on_call = int(nights_on_call)
                trips_made = int(trips_made)
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for hours, nights, and trips.")
                return

            with open(filename, 'r+') as file:
                lines = file.readlines()
                new_entry = f"{date:<20}{time_range:<18}{hours_worked:<20}{nights_on_call:<15}{trips_made:<14}\n"
                data_lines = lines[4:]
                total_index = next((i for i, line in enumerate(data_lines) if line.startswith("Total")), len(data_lines))
                data_lines.insert(total_index, new_entry)
                lines = lines[:4] + data_lines
                file.seek(0)
                file.writelines(lines)

            messagebox.showinfo("Success", "Time entry added successfully.")
            entry_frame.destroy()
            self.show_document_editor(filename)  # Refresh the editor after adding an entry

        save_btn = ttk.Button(entry_frame, text="Save Entry", command=save_entry, style="TButton")
        save_btn.pack(pady=10)

    def remove_time_entry(self, filename, line_idx):
        try:
            with open(filename, 'r') as file:
                lines = file.readlines()

            with open(filename, 'w') as file:
                for idx, line in enumerate(lines):
                    if idx != line_idx + 4:  # Skip 4 header lines
                        file.write(line)

            messagebox.showinfo("Success", "Time entry removed successfully.")
            self.show_document_editor(filename)  # Refresh the editor after removing an entry

        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove time entry: {e}")

    def open_document(self, filename):
        try:
            subprocess.Popen(["notepad.exe", filename])  # Opens the file in Notepad (Windows)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open document: {e}")

    def update_document_totals(self, filename):
        total_hours = 0
        total_nights = 0
        total_trips = 0

        with open(filename, 'r') as file:
            lines = file.readlines()
            data_lines = lines[4:]  # Skip the header lines
            for line in data_lines:
                if line.startswith("Total"):
                    break
                data = line.strip().split()
                if len(data) < 5:
                    continue  # Skip incomplete or malformed lines
                total_hours += float(data[2])
                total_nights += int(data[3])
                total_trips += int(data[4])

        totals = (f"{'-'*83}\n"  # No extra blank line before totals
                  f"{'Total Hours Worked:':<30}{total_hours:<10}\n"
                  f"{'Total Nights On Call:':<30}{total_nights:<10}\n"
                  f"{'Total Trips Made While On Call:':<30}{total_trips:<10}\n")

        with open(filename, 'r+') as file:
            lines = file.readlines()
            data_lines = lines[4:]
            total_index = next((i for i, line in enumerate(data_lines) if line.startswith("Total")), len(data_lines))
            data_lines = data_lines[:total_index]
            lines = lines[:4] + data_lines + [totals]
            file.seek(0)
            file.writelines(lines)
            file.truncate()

if __name__ == "__main__":
    root = tk.Tk()
    app = TimesheetApp(root)
    root.mainloop()
