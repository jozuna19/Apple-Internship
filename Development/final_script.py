#!/usr/local/bin/python3

import sys, getopt, logging, subprocess
from tkinter import Tk, Label, Button, filedialog, messagebox, Radiobutton, StringVar

# Set up the logging configuration
logging.basicConfig(filename='labels.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    import qrcode
    import fpdf
except ImportError:
    logging.error("Required modules not found.")
    print("Requires the following packages:")
    print('python3 -m pip install qrcode fpdf')
    sys.exit(1)

# Scaling function for different label formats
def scaled(size, label_format):
    # Assuming some scaling function exists based on label format
    base_format = (80, 89)  # base format for scaling reference
    scale_factor = min(label_format[0] / base_format[0], label_format[1] / base_format[1])
    return size * scale_factor

# Function to create QR code image file
def make_qr(serial):
    serial_qr_file = "/tmp/qr_serial.png"
    img = qrcode.make(serial)
    img.save(serial_qr_file)
    return serial_qr_file

# Function to generate PDF label
import fpdf

def make_label(serial, project, phase, config, qr_file, product_type='iPhone'):
    file_name = f"{project} - {serial}.pdf"

    # Define label formats for different products
    iphone_label_format = (80, 89)
    watch_label_format = (25, 25)

    # Set parameters based on product type
    if product_type == 'iPhone':
        label_format = iphone_label_format
        qr_size = scaled(23, label_format)
        project_font_size = scaled(13, label_format)
        other_font_size = scaled(10, label_format)
        orientation = 'L'  # Landscape for iPhone label
    else:  # Default to Apple Watch
        label_format = watch_label_format
        qr_size = 13  # Fixed size due to smaller label
        project_font_size = 7  # Smaller font size for the project text
        other_font_size = 5  # Smaller font size for the other text elements
        orientation = 'P'  # Portrait for Watch label

    pdf = fpdf.FPDF(orientation=orientation, unit='mm', format=label_format)
    pdf.add_page()

    if product_type == 'iPhone':
        # iPhone label generation code
        qr_x_center = (label_format[0] - qr_size) / 2 - 24
        qr_y_center = (label_format[1] - qr_size) / 2 + 14
        pdf.rotate(90, qr_x_center, qr_y_center)
        pdf.image(qr_file, x=qr_x_center, y=qr_y_center, w=qr_size, h=qr_size)
        pdf.rotate(0)  # Reset rotation for text
        text_start_x = qr_y_center + qr_size - 57
        text_y_start = qr_x_center + 17
        pdf.rotate(90, text_start_x, text_y_start)
        pdf.set_font('Arial', 'B', project_font_size)
        pdf.text(x=text_start_x, y=text_y_start - 3, txt=serial)
        pdf.set_font('Arial', '', other_font_size)
        pdf.text(x=text_start_x, y=text_y_start + 2, txt=config)
        pdf.text(x=text_start_x, y=text_y_start + 6, txt=phase)
        pdf.text(x=text_start_x, y=text_y_start + 10, txt=project)
        pdf.rotate(0)  # Reset rotation for final output
    else:
        # Apple Watch label generation code
        qr_x = (label_format[0] - qr_size) / 2
        qr_y = -1
        pdf.image(qr_file, x=qr_x, y=qr_y, w=qr_size, h=qr_size)
        text_y_start = qr_y + qr_size + 1.5  # Adjust text start position below QR code
        pdf.set_font('Arial', 'B', project_font_size)
        pdf.text(2, text_y_start, f" {serial}")
        pdf.set_font('Arial', '', other_font_size)
        pdf.text(2, text_y_start + 3, f"{config}")
        pdf.text(2, text_y_start + 6, f"{phase}")
        pdf.text(2, text_y_start + 9, project)

    pdf.output(file_name, "F")
    return file_name


# Function to open file dialog and select TSV file
def browse_files():
    logging.info("Browsing for TSV files...")
    filename = filedialog.askopenfilename(initialdir="/", title="Select a TSV File", filetypes=(("TSV files", "*.tsv"), ("All files", "*.*")))
    if filename:
        logging.info(f"Selected file: {filename}")
    else:
        logging.warning("No file was selected.")
    file_label.config(text=filename)

# Function to generate labels from the selected TSV file
def generate_labels():
    filepath = file_label.cget("text")
    product_type = product_type_var.get()

    if not filepath:
        logging.error("No file selected.")
        messagebox.showerror("Error", "Please select a valid TSV file.")
        return

    try:
        logging.info(f"Reading from file: {filepath}")
        with open(filepath, 'r') as f:
            lines = f.readlines()
            for line in lines[1:]:  # skipping header
                serial, project, phase, config = line.strip().split('\t')
                qr_file = make_qr(serial)
                label_file = make_label(serial, project, phase, config, qr_file, product_type)

                logging.info(f"Sending {label_file} to printer...")
                subprocess.run(["lpr", label_file])

        logging.info("All labels generated successfully.")
        messagebox.showinfo("Success", "Labels generated successfully!")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        messagebox.showerror("Error", f"An error occurred: {e}")

# GUI setup
root = Tk()
root.title("Label Generator")

label = Label(root, text="Select the product type for the labels:")
label.pack(pady=20)

# Radio buttons for product type selection
product_type_var = StringVar(value='iPhone')
Radiobutton(root, text="iPhone", variable=product_type_var, value='iPhone').pack()
Radiobutton(root, text="Apple Watch", variable=product_type_var, value='Apple Watch').pack()

file_label = Label(root, text="No file selected", fg="red")
file_label.pack(pady=10)

browse_button = Button(root, text="Browse", command=browse_files)
browse_button.pack()

generate_button = Button(root, text="Generate Labels", command=generate_labels)
generate_button.pack(pady=20)

# Run the GUI loop
root.mainloop()
