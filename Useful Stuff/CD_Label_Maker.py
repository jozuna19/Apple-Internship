#!/usr/local/bin/python3
import qrcode
import fpdf
import sys
import logging
import subprocess
import argparse

# Check and install required packages
def install_packages():
    try:
        import qrcode
        import fpdf
    except ImportError:
        packages = ["qrcode[pil]", "fpdf"]
        subprocess.check_call([sys.executable, "-m", "pip", "install", *packages])

install_packages()

# Now, import the packages at the top level
from qrcode import QRCode
from fpdf import FPDF

# Logging setup
logging.basicConfig(filename='labels.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
LABEL_FORMAT = (80, 89)  # Regular Label Format, adjusted to match the GUI version
SCALER = 1.6

def scaled(n):
    return n * SCALER

def make_qr(serial):
    serial_qr_file = "/tmp/qr_serial.png"
    qr = QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(serial)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(serial_qr_file)
    return serial_qr_file

def make_label(serial, project, phase, config, qr_file):
    file_name = f"{project} - {serial}.pdf"
    qr_size = scaled(15)
    project_font_size = scaled(10)
    other_font_size = scaled(7)

    pdf = FPDF(orientation='L', unit='mm', format=LABEL_FORMAT)
    pdf.add_page()

    qr_x_center = (LABEL_FORMAT[0] - qr_size) / 2 - 24
    qr_y_center = (LABEL_FORMAT[1] - qr_size) / 2 + 14

    pdf.rotate(90, qr_x_center, qr_y_center)
    pdf.image(qr_file, x=qr_x_center, y=qr_y_center, w=qr_size, h=qr_size)
    pdf.rotate(0)

    text_start_x = qr_y_center + qr_size - 57
    text_y_start = qr_x_center + 17

    pdf.rotate(90, text_start_x, text_y_start)
    pdf.set_font('Arial', 'B', project_font_size)
    pdf.text(x=text_start_x, y=text_y_start - 3, txt=serial)

    pdf.set_font('Arial', '', other_font_size)
    pdf.text(x=text_start_x, y=text_y_start + 2, txt=f"{config}")
    pdf.text(x=text_start_x, y=text_y_start + 6, txt=f"{phase}")
    pdf.text(x=text_start_x, y=text_y_start + 10, txt=f"{project}")
    pdf.rotate(0)

    pdf.output(file_name, "F")
    return file_name

def generate_labels(filepath):
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
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate labels from TSV file.")
    parser.add_argument('filepath', type=str, help='The file path to the TSV input file.')
    args = parser.parse_args()

    logging.info("Script started.")
    generate_labels(args.filepath)
    logging.info("Script finished.")
