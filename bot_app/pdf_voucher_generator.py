import secrets
import string

from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter

from bot_app.db_manager import DBManager

db = DBManager('tattoo_bot_telegram.db')


characters = string.ascii_letters + string.digits
voucher_name = ''.join(secrets.choice(characters) for _ in range(5))


def e_voucher_generator_pdf(chat_id):
    user_voucher = db.get_user_selected_voucher(chat_id)
    user_selected_voucher = user_voucher.split("-")[0]
    select_voucher = db.get_selected_voucher(chat_id)
    user_vouchers = db.get_vouchers_by_user(chat_id)

    for voucher in user_vouchers:
        if select_voucher in voucher or user_selected_voucher in voucher:
            serial_number = voucher[0]
            date_of_buy = voucher[1]
            value = voucher[2]

            input_pdf_path = "bot_app/media/Voucher/E-VOUCHER.pdf"
            output_pdf_path = f"bot_app/media/Voucher/sold_out_vouchers/e_voucher_{voucher_name}.pdf"

            c = canvas.Canvas(output_pdf_path)

            c.drawString(100, 395, f"{value} PLN")                             #COST
            c.drawString(100, 335, date_of_buy)                                     #DATE
            c.drawString(204, 335, serial_number)                                   #SERIAL_NUMBER
            c.save()

            reader = PdfReader(input_pdf_path)
            writer = PdfWriter()
            page = reader.pages[0]
            page.merge_page(PdfReader(output_pdf_path).pages[0])
            writer.add_page(page)
            with open(output_pdf_path, 'wb') as output_file:
                writer.write(output_file)
            return output_pdf_path, serial_number

