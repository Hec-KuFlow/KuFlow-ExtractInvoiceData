import re
import pytesseract
from PIL import Image


def invoice_data_extraction(image):
    data_extracted = extract_invoice_data(image)
    final_data = get_final_data(data_extracted)
    return final_data


def extract_invoice_data(image):
    # Open the image using Pillow library
    with Image.open(image) as img:
        # Convert the image into text using pytesseract library
        pytesseract.pytesseract.tesseract_cmd = (r"C:\Program Files\Tesseract-OCR\tesseract.exe")
        invoice_data = pytesseract.image_to_string(img)
    return invoice_data


def get_text_between(main_string, start_word, end_word):
    start = main_string.find(start_word) + len(start_word)
    end = main_string.find(end_word)
    return main_string[start:end]


def get_final_data(data):
    patron_fecha = r"\b\d{1,2}/\d{1,2}/\d{4}\b"
    patron_total = r"\bTOTAL\D*(\d+(?:[,.]\d+)?)(?:\s*(?:€|\$|USD|EUR))?\b"

    client = get_text_between(data, "www.quiasmoeditorial.es", "C/ ").strip()
    invoice_number = get_text_between(data, "Factura ", " |").strip()

    invoice_date = re.search(patron_fecha, data).group(0)
    invoice_total = re.findall(patron_total, data)[1]

    return client, invoice_number, invoice_date, invoice_total
