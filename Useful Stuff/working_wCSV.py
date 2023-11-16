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
    base_format = (80, 89)  # base format for scaling reference
    scale_factor = min(label_format[0] / base_format[0], label_format[1] / base_format[1])
    return size * scale_factor

# Function to create QR code image file
def make_qr(config):
    serial_qr_file = "/tmp/qr_serial.png"
    img = qrcode.make(config)
    img.save(serial_qr_file)
    return serial_qr_file

# Function to generate PDF label
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
        qr_x_center = (label_format[0] - qr_size) / 2 - 24
        qr_y_center = (label_format[1] - qr_size) / 2 + 14
        pdf.rotate(90, qr_x_center, qr_y_center)
        pdf.image(qr_file, x=qr_x_center, y=qr_y_center, w=qr_size, h=qr_size)
        pdf.rotate(0)  # Reset rotation for text
        text_start_x = qr_y_center + qr_size - 57
        text_y_start = qr_x_center + 17
        pdf.rotate(90, text_start_x, text_y_start)
        pdf.set_font('Arial', 'B', project_font_size)
        pdf.text(x=text_start_x, y=text_y_start - 3, txt=project)
        pdf.set_font('Arial', '', other_font_size)
        pdf.text(x=text_start_x, y=text_y_start + 2, txt=serial)
        pdf.text(x=text_start_x, y=text_y_start + 6, txt=config)
        pdf.rotate(0)  # Reset rotation for final output
    else:
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

# Function to open file dialog and select CSV file
def browse_files():
    logging.info("Browsing for CSV files...")
    filename = filedialog.askopenfilename(initialdir="/", title="Select a CSV File", filetypes=(("CSV files", "*.csv"), ("All files", "*.*")))
    if filename:
        logging.info(f"Selected file: {filename}")
        generate_labels(filename)
    else:
        logging.warning("No file selected.")

# Function to generate labels from the selected CSV file
def generate_labels(filename, product_type='iPhone'):
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()

        for line in lines[1:]:  # skipping header
            project, phase, config, serial = line.strip().split(',')
            qr_file = make_qr(serial)
            label_file = make_label(serial, project, phase, config, qr_file, product_type)
            logging.info(f"Generated label: {label_file}")

            # Send label to printer
            logging.info(f"Sending {label_file} to printer...")
            subprocess.run(["lpr", label_file])

        messagebox.showinfo("Success", "Labels generated and sent to printer successfully.")
    except Exception as e:
        logging.error(f"Error generating labels: {e}")
        messagebox.showerror("Error", f"Error generating labels: {e}")


# GUI setup
root = Tk()
root.title("Label Generator")

label = Label(root, text="Select a CSV File to Generate Labels")
label.grid(columnspan=3, row=0, pady=20)

browse_button = Button(root, text="Browse", command=browse_files)
browse_button.grid(row=1, column=0, pady=10)

product_type_var = StringVar(value='iPhone')
iphone_rb = Radiobutton(root, text="iPhone", variable=product_type_var, value='iPhone')
iphone_rb.grid(row=1, column=1)
watch_rb = Radiobutton(root, text="Apple Watch", variable=product_type_var, value='Watch')
watch_rb.grid(row=1, column=2)

exit_button = Button(root, text="Exit", command=root.quit)
exit_button.grid(row=2, columnspan=3, pady=10)

root.mainloop()
