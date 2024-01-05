from PyPDF2 import PdfReader, PdfWriter
import fitz
from pprint import pprint

def getDataFromAI(label: str):
    return 'AI'

def updateFields(page: fitz.Page):
    w = page.first_widget
    while w is not None:
        print(w)
        print(w.field_label)
        if w.field_label is None:
            print("No field label")
            w = w.next
            continue
        value = getDataFromAI(w.field_label)
        w.field_value = value # type: ignore
        w.update()
        w = w.next

def listFitz(pdf_file):
    doc = fitz.Document(pdf_file)
    page0: fitz.Page = doc.load_page(0)
    if page0 is None:
        return
    
    updateFields(page0)

    doc.save('./forms/i-765-filled-fitz.pdf')

listFitz('./forms/i-765-filled.pdf')

def list2(pdf_file):
    pdf = PdfReader(open(pdf_file, 'rb'))
    return pdf.get_form_text_fields()

# fields = list2('./forms/i-765.pdf')

def list_form_fields(pdf_file):
    pdf = PdfReader(open(pdf_file, 'rb'))
    return pdf.get_fields()

# pdf_fields = list_form_fields('./forms/i-765.pdf')
# if pdf_fields:
#   pprint(pdf_fields)

def fill_pdf(input_pdf_path, output_pdf_path, data_dict):
    pdf_reader = PdfReader(open(input_pdf_path, 'rb'))
    pdf_writer = PdfWriter()

    # Copy the pages from the original PDF to the new one
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        pdf_writer.add_page(page)

    # Update the form fields on every page
    for page_num in range(len(pdf_writer.pages)):
      pdf_writer.update_page_form_field_values(pdf_writer.pages[page_num], data_dict)

    # Write the output PDF
    with open(output_pdf_path, 'wb') as output_pdf_file:
        pdf_writer.write(output_pdf_file)

# import data from data.json
import json

with open('./data.json') as f:
    data = json.load(f)
    fill_pdf('./forms/i-765.pdf', './forms/i-765-filled.pdf', data)
