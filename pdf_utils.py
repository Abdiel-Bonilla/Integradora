from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import code39
from io import BytesIO
from flask import send_file

def generar_pdf(venta):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle("Venta")

    # Ruta de la imagen
    image_path = 'static/assets/Diconsa.jpg'  # Asegúrate de colocar la ruta correcta de la imagen

    # Tamaño de la imagen y posición
    image_width = 100
    image_height = 50
    pdf.drawImage(image_path, x=250, y=730, width=image_width, height=image_height)  # Ajusta la posición según sea necesario

    # Encabezado
    pdf.setFont("Helvetica-Bold", 24)
    pdf.setFillColor(colors.black)
    pdf.drawCentredString(300, 690, "Tienda Diconsa")  # Ajusta la posición según el tamaño de la imagen

    # Línea de separación
    pdf.setStrokeColor(colors.blue)
    pdf.setLineWidth(2)
    pdf.line(50, 675, 550, 675)  # Dibuja una línea horizontal para separar el encabezado

    # Datos de la venta
    pdf.setFont("Helvetica-Bold", 12)
    pdf.setFillColor(colors.black)
    pdf.drawCentredString(300, 650, "Detalles de la Venta")

    # Datos de la venta
    pdf.setFont("Helvetica-Bold", 10)
    pdf.setFillColor(colors.black)

    # Configurar las etiquetas y datos
    labels = [
        "ID Venta:", "Fecha:", "Hora:", "Usuario:", "Cargo:", 
        "Producto:", "Cantidad:", "Total:"
    ]
    data = [
        venta[0], venta[1], venta[2], venta[3], venta[4], 
        venta[5], venta[6], venta[7]
    ]

    # Calcular la posición central para las etiquetas y los datos
    num_lines = len(labels)
    line_height = 20
    start_y = 620  # Posición inicial en Y

    # Calcular la posición horizontal central
    x_center = 300
    max_label_width = max(pdf.stringWidth(label, "Helvetica-Bold", 10) for label in labels)
    max_data_width = max(pdf.stringWidth(str(data[i]), "Helvetica-Bold", 10) for i in range(len(data)))

    for i in range(num_lines):
        label = labels[i]
        data_value = str(data[i])
        
        # Calcular posiciones centradas
        label_x = x_center - (max_label_width + max_data_width + 10) / 2
        data_x = label_x + max_label_width + 10
        
        pdf.drawString(label_x, start_y - i * line_height, label)
        pdf.drawString(data_x, start_y - i * line_height, data_value)

    # Línea de separación
    pdf.setStrokeColor(colors.blue)
    pdf.setLineWidth(2)
    pdf.line(50, start_y - num_lines * line_height - 10, 550, start_y - num_lines * line_height - 10)  # Dibuja una línea horizontal para separar los datos del código de barras

    # Título del código de barras
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawCentredString(300, start_y - num_lines * line_height - 30, "Código de Barras")

    # Espacio adicional antes del código de barras
    barcode_title_y = start_y - num_lines * line_height - 50  # Ajusta este valor según el espacio deseado

    # Agregar código de barras
    barcode_value = str(venta[0])  # Usar el ID de la venta como valor del código de barras
    barcode = code39.Extended39(barcode_value, barHeight=60, stop=1)  # Aumentar la altura del código de barras
    barcode_width = barcode.width
    barcode.drawOn(pdf, 300 - barcode_width / 2, barcode_title_y - 70)  # Ajusta la posición vertical del código de barras

    # Línea de separación antes de la información adicional
    pdf.setStrokeColor(colors.blue)
    pdf.setLineWidth(2)
    pdf.line(50, barcode_title_y - 100, 550, barcode_title_y - 100)  # Dibuja una línea horizontal para separar el código de barras de la información adicional

    # Información adicional
    pdf.setFont("Helvetica-Bold", 12)
    pdf.setFillColor(colors.black)
    pdf.drawCentredString(300, barcode_title_y - 120, "Información Adicional")

    # Información adicional
    pdf.setFont("Helvetica", 10)
    pdf.drawCentredString(300, barcode_title_y - 140, "Dirección: Calle 20 de Noviembre18, Cuarta Secc,")
    pdf.drawCentredString(300, barcode_title_y - 155, "90495 San José Teacalco Tlaxcala, México")
    pdf.drawCentredString(300, barcode_title_y - 170, "Horario: 8:00 a.m - 9:30 p.m")
    pdf.drawCentredString(300, barcode_title_y - 185, "Teléfono: (+52) 241-118-2178")

    # Pie de página
    pdf.setFont("Helvetica", 10)
    pdf.drawCentredString(300, 40, "¡Gracias por su compra!")

    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    return buffer
