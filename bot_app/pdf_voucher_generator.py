import secrets
import string

from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter

from bot_app.db_manager import DBManager

db = DBManager('tattoo_bot_telegram.db')


characters = string.ascii_letters + string.digits
voucher_name = ''.join(secrets.choice(characters) for _ in range(5))


def e_voucher_generator_pdf(chat_id):
    """
    e_voucher_generator_pdf Function Description

    The `e_voucher_generator_pdf` function generates an electronic voucher PDF file based on the user's selected
    voucher information. It retrieves the user's selected voucher details from the database, including the serial
    number, date of purchase, and voucher value. It then creates a customized PDF voucher by overlaying this
    information onto a pre-designed template.

    Functionality:

    - Retrieve User Voucher Information: Retrieves the user's selected voucher details from the database using
    the provided `chat_id`. Extracts the serial number, date of purchase, and voucher value from the voucher data.
    - PDF Generation: Utilizes the `canvas.Canvas` module from the `reportlab` library to draw text elements onto a
    PDF template. Inserts the voucher value, date of purchase, and serial number into designated positions on the
    template.
    - PDF Overlay: Merges the customized voucher template with the pre-designed voucher template using
    the `merge_page` method from the `PyPDF2` library.
    - Save PDF: Saves the generated electronic voucher PDF
    file to the specified output path.
    - Return Path and Serial Number: Returns the file path of the generated PDF voucher
    and its corresponding serial number.

    Usage:

    - Invoke this function when generating electronic vouchers for users in response to specific actions or requests.
    - Ensure that the user's selected voucher information is retrieved from the database before calling this
    function.
    - Customize the PDF template layout and design to match the desired appearance of the electronic
    vouchers.
    - Update the input and output file paths for the PDF template and generated vouchers based on the file
    structure of your application. - Handle any errors or exceptions that may occur during the PDF generation
    process, such as missing voucher data or file I/O issues.

    Note: This function relies on external libraries (`reportlab`, `PyPDF2`) for PDF generation and manipulation.
    Make sure these libraries are installed and accessible within your Python environment.

    Feel free to integrate and adapt this function to suit the specific requirements of your voucher generation
    system within your Telegram bot application!"""

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


