import subprocess
import sys

try:
    import pypdf
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pypdf"])
    import pypdf

from pypdf import PdfReader
reader = PdfReader('c:/laragon/www/dsp-attrition-app/Data_Attrition_Jaya_Maju.pdf')
text = ""
for page in reader.pages:
    text += page.extract_text() + "\n"

with open('c:/laragon/www/dsp-attrition-app/pdf_content.txt', 'w', encoding='utf-8') as f:
    f.write(text)
print("PDF extracted successfully.")
