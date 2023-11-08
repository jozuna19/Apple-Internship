#!/usr/local/bin/python3
import sys, logging, subprocess
from tkinter import Tk, Label, Button, filedialog, messagebox
import qrcode
import fpdf

# Logging setup
logging.basicConfig(filename='labels.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
LABEL_FORMAT = (89,28)
SCALER = 1.3

def scaled(n):
    return n * SCALER

def make_qr(serial):
    serial_qr_file = "/tmp/qr_serial.png"
    img = qrcode.make(serial)
    img.save(serial_qr_file)
    return serial_qr_file

# Assuming scaled is a function you've defined to scale measurements
def scaled(value):
    return value  # Replace this with your scaling function or formula

# Constants for label size
LABEL_WIDTH = 89  # label width in mm (4 inches)
LABEL_HEIGHT = 28  # label height in mm (3 inches)
LABEL_FORMAT = (LABEL_WIDTH, LABEL_HEIGHT)

def make_qr(serial):
    serial_qr_file = "/tmp/qr_serial.png"
    img = qrcode.make(serial)
    img.save(serial_qr_file)
    return serial_qr_file

def make_label(serial, project, phase, config, qr_file):
    file_name = f"{project} - {serial}.pdf"
    qr_size = scaled(15)
    project_font_size = scaled(9)
    other_font_size = scaled(7)

    pdf = fpdf.FPDF(orientation='L', unit='mm', format=LABEL_FORMAT)
    pdf.add_page()

    qr_x_center = (LABEL_FORMAT[0] - qr_size) / 2
    qr_y_center = (LABEL_FORMAT[1] - qr_size) / 2 - 31

    pdf.image(qr_file, x=qr_x_center, y=qr_y_center, w=qr_size, h=qr_size)

    text_start_x = qr_x_center + qr_size + 2
    text_y_start = qr_y_center + 6

    pdf.set_font('Arial', 'B', project_font_size)
    pdf.text(x=text_start_x, y=text_y_start, txt=f"{serial}")

    pdf.set_font('Arial', '', other_font_size)
    pdf.text(x=text_start_x, y=text_y_start + 3, txt=f"{config}")
    pdf.text(x=text_start_x, y=text_y_start + 6, txt=f"{project}")
    pdf.text(x=text_start_x, y=text_y_start + 9, txt=f"{phase}")


class LabelApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Label Generator")

        self.label = Label(self.master, text="Select the TSV file containing label data")
        self.label.pack(pady=20)

        self.browse_btn = Button(self.master, text="Browse", command=self.browse_files)
        self.browse_btn.pack(pady=20)

        self.file_label = Label(self.master, text="")
        self.file_label.pack(pady=10)

        self.generate_btn = Button(self.master, text="Generate Labels", command=self.generate_labels)
        self.generate_btn.pack(pady=20)

    def browse_files(self):
        filename = filedialog.askopenfilename(initialdir="/", title="Select a TSV File", filetypes=(("TSV files", "*.tsv"), ("All files", "*.*")))
        if filename:
            logging.info(f"Selected file: {filename}")
        else:
            logging.warning("No file was selected.")
        self.file_label.config(text=filename)

    def generate_labels(self):
        filepath = self.file_label.cget("text")
        if not filepath:
            logging.error("No file selected.")
            messagebox.showerror("Error", "Please select a valid TSV file.")
            return

        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()
                for line in lines[1:]:
                    serial, project, phase, config = line.strip().split('\t')
                    serial = serial.strip()
                    project = project.strip().replace('/', '_')
                    phase = phase.strip().replace('/', '_')
                    config = config.strip().replace('/', '_')

                    logging.info(f"Generating label for Serial: {serial}, Project: {project}, Phase: {phase}, Config: {config}")
                    qr_file = make_qr(serial)
                    label_file = make_label(serial, project, phase, config, qr_file)

                    logging.info(f"Sending {label_file} to printer...")
                    subprocess.run(["lpr", label_file])

            logging.info("All labels generated successfully.")
            messagebox.showinfo("Success", "Labels generated successfully!")
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}")

if __name__ == "__main__":
    logging.info("Script started.")
    root = Tk()
    app = LabelApp(root)
    root.mainloop()
    logging.info("Script finished.")
