import qrcode

# The URL you want the QR code to point to
url = "https://cyclesync-veritwin.onrender.com"

# Generate the QR code
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=10,
    border=4,
)
qr.add_data(url)
qr.make(fit=True)

# Create and save the image
img = qr.make_image(fill_color="black", back_color="white")
img.save("my_website_qr.png")