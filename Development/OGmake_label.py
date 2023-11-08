#!/usr/local/bin/python3

import sys, getopt

try:
    import qrcode
    import fpdf
    
except:
    print("Requires the following packages:")
    print( 'python3 -m pip install --upgrade --index-url "https://pypi.apple.com/simple" qrcode' )
    print( 'python3 -m pip install --upgrade --index-url "https://pypi.apple.com/simple" fpdf' )
    exit(1)

help_message="make_label.py -s SERIAL -p PROJECT -d DEVELOPMENT_PHASE -c config"

def scaled(n):
    scaler = 1.3
    return n * scaler
    
def make_qr(serial):
    serial_qr_file = "/tmp/qr_serial.png"
    img = qrcode.make( serial )

    # Saving as an image file
    img.save( serial_qr_file )
    return serial_qr_file

def make_label(serial, project, phase, config, qr_file, label_format):
    file_name = f"{project} - {serial}.pdf"
    pdf = fpdf.FPDF(format=label_format)
    pdf.add_page()

    # Adjust QR code size and positions based on label format
    if label_format == (54, 25):  # Original label size
        qr_size = scaled(20)
        text_start_x = scaled(13)
        project_font_size = scaled(12)
        other_font_size = scaled(8)
    else:  # Apple Watch label size
        qr_size = scaled(10)  # smaller QR size for the 1x1 label
        text_start_x = qr_size + 1  # start just after the QR
        project_font_size = scaled(6)  # smaller font sizes
        other_font_size = scaled(4)  # smaller font sizes

    pdf.image(
        qr_file,
        x=scaled(0),
        y=scaled(0),
        w=qr_size,
        h=qr_size,
    )

    pdf.set_font('Helvetica', 'B', project_font_size)
    pdf.text(x=text_start_x, y=scaled(5), txt=project)

    pdf.set_font('Helvetica', '', other_font_size)
    pdf.text(x=text_start_x, y=scaled(8), txt=f"{phase}")
    pdf.text(x=text_start_x, y=scaled(11), txt=f"{serial}")
    pdf.text(x=text_start_x, y=scaled(14), txt=f"{config}")

    pdf.output(file_name, "F")
    return file_name


def main(argv):
    
    serial = None
    project = None
    phase = ""
    try:
        opts, args = getopt.getopt(argv,"hs:p:d:c:")
        # Reject invalid args
    except getopt.GetoptError:
        print(help_message)
        exit(1)
        
    for opt, arg in opts:
        if opt == '-h':
            print (help_message)
            sys.exit()
        elif opt in ( "-s" ):
            serial = arg
        elif opt in ( "-p" ):
            project = arg
        elif opt in ( "-d" ):
            phase = arg
        elif opt in ( "-c" ):
            config = arg
            
    if not serial or not project:
        print(help_message)
        exit(1)
    
    serial = serial.strip()
    project = project.strip().replace( '/', '_' )
    phase = phase.strip().replace( '/', '_' )
    config = config.strip().replace( '/', '_' )
    
    qr_file = make_qr(serial)
    file = make_label(
        serial=serial,
        project=project,
        phase=phase,
        config=config,
        qr_file=qr_file,
        )
    
    print( f"{file}" )
    
if __name__ == "__main__":
    main(sys.argv[1:])
