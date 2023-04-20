from dataclasses import dataclass
import re
from kuflow_rest import KuFlowRestClient
from kuflow_rest import models
import pytesseract
from PIL import Image
from temporalio import activity
import io


@dataclass
class InvoiceDataExtractionRequest:
    task_id: str


@dataclass
class InvoiceDataExtractionResponse:
    client: str
    invoice_number: str
    invoice_date: str
    invoice_total: str


class InvoiceActivities:
    def __init__(self, kuflow_client: KuFlowRestClient) -> None:
        self._kuflow_client = kuflow_client
        self.activities = [self.invoice_data_extraction]

    @activity.defn
    async def invoice_data_extraction(self, request: InvoiceDataExtractionRequest) -> InvoiceDataExtractionResponse:
        task = self._kuflow_client.task.retrieve_task(id=request.task_id)
        document: models.TaskElementValueDocument = task.element_values["uploadedFile"][0]

        document_file = (
            self._kuflow_client.task.actions_task_download_element_value_document(
                id=request.task_id, document_id=document.value.id)
        )

        byte_data = b"".join(document_file)
        binary_stream = io.BytesIO(byte_data)
        data_extracted = self.extract_invoice_data(binary_stream)
        final_data = self.get_final_data(data_extracted)

        return InvoiceDataExtractionResponse(
            client=final_data[0],
            invoice_number=final_data[1],
            invoice_date=final_data[2],
            invoice_total=final_data[3],
        )

    def extract_invoice_data(self, image):
        # Open the image using Pillow library
        with Image.open(image) as img:
            # Convert the image into text using pytesseract library
            pytesseract.pytesseract.tesseract_cmd = (r"C:\Program Files\Tesseract-OCR\tesseract.exe")
            invoice_data = pytesseract.image_to_string(img)
        return invoice_data

    def get_text_between(self, main_string, start_word, end_word):
        start = main_string.find(start_word) + len(start_word)
        end = main_string.find(end_word)
        return main_string[start:end]

    def get_final_data(self, data):
        patron_fecha = r"\b\d{1,2}/\d{1,2}/\d{4}\b"
        patron_total = r"\bTOTAL\D*(\d+(?:[,.]\d+)?)(?:\s*(?:€|\$|USD|EUR))?\b"

        client = self.get_text_between(data, "www.quiasmoeditorial.es", "C/ ").strip()
        invoice_number = self.get_text_between(data, "Factura ", " |").strip()

        invoice_date = re.search(patron_fecha, data).group(0)
        invoice_total = re.findall(patron_total, data)[1]

        return client, invoice_number, invoice_date, invoice_total
