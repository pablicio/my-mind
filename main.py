# main.py

from etl.extract.pdf_to_text import convert_PDF_to_text
import easyocr

reader = easyocr.Reader(['en', 'pt'])  # idiomas suportados
pdf_path = 'data/raw/A-Brief-Introduction-to-Singapore.pdf'      # caminho para o PDF

text = convert_PDF_to_text(reader, pdf_path)

print("Texto extraído:")
print(text)
