import os
import sys
import logging
import argparse
from adobe.pdfservices.operation.auth.service_principal_credentials import ServicePrincipalCredentials
from adobe.pdfservices.operation.exception.exceptions import ServiceApiException, ServiceUsageException, SdkException
from adobe.pdfservices.operation.pdf_services import PDFServices
from adobe.pdfservices.operation.pdf_services_media_type import PDFServicesMediaType
from adobe.pdfservices.operation.pdfjobs.jobs.extract_pdf_job import ExtractPDFJob
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_element_type import ExtractElementType
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_pdf_params import ExtractPDFParams
from adobe.pdfservices.operation.pdfjobs.result.extract_pdf_result import ExtractPDFResult

# Initialize the logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_pdf_service_credentials():
    client_id = os.getenv('PDF_SERVICES_CLIENT_ID')
    client_secret = os.getenv('PDF_SERVICES_CLIENT_SECRET')

    if not client_id or not client_secret:
        raise ValueError("PDF_SERVICES_CLIENT_ID and PDF_SERVICES_CLIENT_SECRET environment variables must be set.")

    return ServicePrincipalCredentials(client_id, client_secret)


def extract_text_from_pdf(input_pdf_path: str, output_zip_path: str):
    try:
        logging.info(f"Attempting to extract text from {input_pdf_path}")

        credentials = get_pdf_service_credentials()
        pdf_services = PDFServices(credentials)

        # Upload the PDF file
        with open(input_pdf_path, 'rb') as file:
            input_asset = pdf_services.upload(file, mime_type=PDFServicesMediaType.PDF)

        # Define extraction parameters
        extract_pdf_params = ExtractPDFParams(elements_to_extract=[ExtractElementType.TEXT])
        extract_pdf_job = ExtractPDFJob(input_asset=input_asset, extract_pdf_params=extract_pdf_params)

        # Submit the job and get the result
        location = pdf_services.submit(extract_pdf_job)
        pdf_services_response = pdf_services.get_job_result(location, ExtractPDFResult)

        # Get the content from the resulting asset
        result_asset = pdf_services_response.get_result().get_resource()
        stream_asset = pdf_services.get_content(result_asset)

        # Save the result to a file
        with open(output_zip_path, "wb") as file:
            file.write(stream_asset.get_input_stream())

        logging.info(f"✅ Successfully extracted text. Output saved to: {output_zip_path}")

    except (ServiceApiException, ServiceUsageException, SdkException, ValueError) as e:
        logging.error(f"An exception occurred: {e}", exc_info=True)
    except FileNotFoundError:
        logging.error(f"Input PDF file not found at: {input_pdf_path}", exc_info=True)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract text from a PDF using Adobe PDF Services API.")
    parser.add_argument("input_pdf", type=str, help="Path to the input PDF file")
    parser.add_argument("-o", "--output", type=str, default="extractTextInfoFromPDF.zip",
                        help="Output ZIP file path (default: extractTextInfoFromPDF.zip)")
    args = parser.parse_args()

    input_pdf = args.input_pdf
    output_zip = args.output

    extract_text_from_pdf(input_pdf, output_zip)

