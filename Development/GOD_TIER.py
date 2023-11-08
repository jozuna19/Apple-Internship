#!/usr/local/bin/python3

import sys
import qrcode
import fpdf
import subprocess
import os
import tempfile

help_message = "Usage: make_label.py -s SERIAL -p PROJECT -d DEVELOPMENT_PHASE -c config OR make_label.py --file FILE_PATH"

def scaled(n):
    scaler = 1.3
    return n * scaler
def get_label_format():
    user_input = input("Are you printing a label for an Apple Watch? (y/n): ").strip().lower()
    if user_input == 'y':
        # Format for Apple Watch
        return (28, 28)
    else:
        # Default format
        return (54, 25)

def make_qr(serial):
    serial_qr_file = "/tmp/qr_serial.png"
    img = qrcode.make(serial)
    img.save(serial_qr_file)
    return serial_qr_file

def make_label(serial, project, phase, config, qr_file, label_format):
    file_name = f"{project} - {serial}.pdf"
    pdf = fpdf.FPDF(format=label_format)
    pdf.add_page()
    pdf.image(
        qr_file, 
        x=scaled(0),
        y=scaled(0),
        w=scaled(13),
        h=scaled(13),
    )
    pdf.set_font('Helvetica', 'B', scaled(12))
    pdf.text(x=scaled(13), y=scaled(5), txt=project)
    pdf.set_font('Helvetica', '', scaled(8))
    pdf.text(x=scaled(13), y=scaled(8), txt=f"{phase}")
    pdf.text(x=scaled(13), y=scaled(11), txt=f"{serial}")
    pdf.text(x=scaled(2), y=scaled(14), txt=f"{config}")
    pdf.output(file_name, "F")
    return file_name

def print_labels(file_name, label_format):
    media_size = "Custom.1x1inch" if label_format == (28, 28) else "Custom.25x54mm"
    subprocess.run([
        "lpr", 
        "-P", "DYMO_LabelWriter_550_Turbo", 
        "-o", "orientation-requested=4", 
        "-o", f"media={media_size}", 
        file_name
    ])

def main(argv):
    import getopt
    try:
        opts, args = getopt.getopt(argv, "hs:p:d:c:", ["file="])
    except getopt.GetoptError:
        print(help_message)
        exit(1)

    file_path = None
    serial = None
    project = None
    phase = ""
    config = ""

    for opt, arg in opts:
        if opt == '-h':
            print(help_message)
            exit(0)
        elif opt == "--file":
            file_path = arg
        elif opt in ("-s"):
            serial = arg
        elif opt in ("-p"):
            project = arg
        elif opt in ("-d"):
            phase = arg
        elif opt in ("-c"):
            config = arg

    label_format = get_label_format()

    if file_path:
        process_file(file_path, label_format)
    else:
        if not serial or not project:
            print(help_message)
            exit(1)
        
        serial = serial.strip()
        project = project.strip().replace('/', '_')
        phase = phase.strip().replace('/', '_')
        config = config.strip().replace('/', '_')

        qr_file = make_qr(serial)
        file = make_label(serial, project, phase, config, qr_file, label_format)
        print(file)
        print_labels(file, label_format)

def process_file(file_path, label_format):
    if not os.path.exists(file_path):
        print(f"File {file_path} not found!")
        exit(1)
    
    label_directory = tempfile.mkdtemp(prefix="labels_", dir=os.path.expanduser("~/Desktop"))
    print(f"Label directory: {label_directory}")

    with open(file_path, 'r') as f:
        lines = f.readlines()[1:]

    for line in lines:
        project, phase, config, serial = line.strip().split('\t')
        file_name = make_label(serial, project, phase, config, make_qr(serial), label_format)
        print(file_name)
        print_labels(file_name, label_format)

if __name__ == "__main__":
    main(sys.argv[1:])
