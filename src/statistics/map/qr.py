import qrcode

url = "https://irinarubleva.github.io/AIRLINES_lab/src/statistics/map/flights_map.html"
qr = qrcode.QRCode(version=1, box_size=10, border=5)
qr.add_data(url)
qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white")
img.save("qr_code.png")
print(f"QR-код сохранен: qr_code.png")
print(f"Ссылка: {url}")


