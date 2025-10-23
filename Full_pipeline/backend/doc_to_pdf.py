
import os
import logging
import argparse
from adobe.pdfservices.operation.auth.service_principal_credentials import ServicePrincipalCredentials
from adobe.pdfservices.operation.exception.exceptions import ServiceApiException, ServiceUsageException, SdkException
from adobe.pdfservices.operation.pdf_services import PDFServices
from adobe.pdfservices.operation.pdf_services_media_type import PDFServicesMediaType
from adobe.pdfservices.operation.pdfjobs.jobs.create_pdf_job import CreatePDFJob
from adobe.pdfservices.operation.pdfjobs.result.create_pdf_result import CreatePDFResult

logging.basicConfig(level=logging.INFO)

def convert_doc_to_pdf(input_doc_path, output_pdf_path):
    """
    Convert a document (Word, Excel, PowerPoint, TXT, RTF) to PDF using Adobe PDF Services API.
    """
    try:
        client_id = os.getenv("PDF_SERVICES_CLIENT_ID")
        client_secret = os.getenv("PDF_SERVICES_CLIENT_SECRET")

        if not client_id or not client_secret:
            raise ValueError("PDF_SERVICES_CLIENT_ID and PDF_SERVICES_CLIENT_SECRET environment variables must be set.")

        credentials = ServicePrincipalCredentials(client_id, client_secret)
        pdf_services = PDFServices(credentials)

        ext = os.path.splitext(input_doc_path)[1].lower()
        media_types = {
            '.docx': PDFServicesMediaType.DOCX,
            '.doc': PDFServicesMediaType.DOC,
            '.xlsx': PDFServicesMediaType.XLSX,
            '.xls': PDFServicesMediaType.XLS,
            '.pptx': PDFServicesMediaType.PPTX,
            '.ppt': PDFServicesMediaType.PPT,
            '.txt': PDFServicesMediaType.TXT,
            '.rtf': PDFServicesMediaType.RTF
        }

        if ext not in media_types:
            raise ValueError(f"Unsupported file type: {ext}")

        media_type = media_types[ext]

        logging.info(f"Uploading {input_doc_path}...")
        with open(input_doc_path, 'rb') as file:
            input_asset = pdf_services.upload(file, media_type)

        create_pdf_job = CreatePDFJob(input_asset)
        logging.info("Creating PDF...")
        location = pdf_services.submit(create_pdf_job)
        pdf_services_response = pdf_services.get_job_result(location, CreatePDFResult)
        result_asset = pdf_services_response.get_result().get_asset()

        logging.info(f"Saving PDF to {output_pdf_path}...")
        stream_asset = pdf_services.get_content(result_asset)
        with open(output_pdf_path, "wb") as file:
            file.write(stream_asset.get_input_stream())

        logging.info(f"Successfully created PDF: {output_pdf_path}")
        return True

    except (ServiceApiException, ServiceUsageException, SdkException) as e:
        logging.error(f"Adobe PDF Services error: {e}")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert a document to PDF using Adobe PDF Services API")
    parser.add_argument("input_doc", type=str, help="Path to the input document (Word, Excel, PowerPoint, TXT, RTF)")
    parser.add_argument("output_pdf", type=str, help="Path to save the converted PDF")
    args = parser.parse_args()

    success = convert_doc_to_pdf(args.input_doc, args.output_pdf)
    if success:
        print("Document conversion completed successfully!")
    else:
        print("Document conversion failed!")
        exit(1)

