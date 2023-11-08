#!/usr/local/bin/python3

import sys, getopt, logging, subprocess
from tkinter import Tk, Label, Button, filedialog, messagebox

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

def scaled(n):
    scaler = 1.6
    return n * scaler

def make_qr(serial):
    serial_qr_file = "/tmp/qr_serial.png"
    img = qrcode.make(serial)
    img.save(serial_qr_file)
    return serial_qr_file

def make_label(serial, project, phase, config, qr_file):
    file_name = f"{project} - {serial}.pdf"

    # Determine label format
    label_format = (80,89)  #Regular Label Format
    if label_format == (80,89):
        qr_size = scaled(15)
        project_font_size = scaled(10)
        other_font_size = scaled(7)
    else:
        label_format = (25,25)

    pdf = fpdf.FPDF(orientation='L', unit='mm', format=label_format)
    pdf.add_page()

    # Positioning for rotated QR code and text
    qr_x_center = (label_format[0] - qr_size) / 2 - 24 # Centering the QR code horizontally
    qr_y_center = (label_format[1] - qr_size) / 2 + 14 # Centering the QR code vertically

    # Rotate the QR code by 90 degrees
    pdf.rotate(90, qr_x_center, qr_y_center)
    pdf.image(
        qr_file,
        x=qr_x_center,
        y=qr_y_center,
        w=qr_size,
        h=qr_size,
    )
    pdf.rotate(0)  # Reset rotation for the text

    # Positioning for rotated text
    text_start_x = qr_y_center + qr_size - 57 # Positioning text below the QR code (since it will be rotated)
    text_y_start = qr_x_center + 17  # Starting Y position of text to the left of the QR code (since it will be rotated)

    # Rotate the text by 90 degrees
    pdf.rotate(90, text_start_x, text_y_start)
    pdf.set_font('Arial', 'B', project_font_size)
    pdf.text(x=text_start_x, y=text_y_start - 3, txt=serial)

    pdf.set_font('Arial', '', other_font_size)
    pdf.text(x=text_start_x, y=text_y_start + 2, txt=f"{config}")
    pdf.text(x=text_start_x, y=text_y_start + 6, txt=f"{phase}")
    pdf.text(x=text_start_x, y=text_y_start + 10, txt=f"{project}")
    pdf.rotate(0)  # Reset rotation

    pdf.output(file_name, "F")
    return file_name


def browse_files():
    logging.info("Browsing for TSV files...")
    filename = filedialog.askopenfilename(initialdir="/", title="Select a TSV File", filetypes=(("TSV files", "*.tsv"), ("All files", "*.*")))
    if filename:
        logging.info(f"Selected file: {filename}")
    else:
        logging.warning("No file was selected.")
    file_label.config(text=filename)
    return None

def generate_labels():
    filepath = file_label.cget("text")
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

# GUI setup
root = Tk()
root.title("Label Generator")

label = Label(root, text="Select the TSV file containing label data")
label.pack(pady=20)

browse_btn = Button(root, text="Browse", command=browse_files)
browse_btn.pack(pady=20)

file_label = Label(root, text="")
file_label.pack(pady=10)

generate_btn = Button(root, text="Generate Labels", command=generate_labels)
generate_btn.pack(pady=20)

if __name__ == "__main__":
    logging.info("Script started.")
    root.mainloop()
    logging.info("Script finished.")