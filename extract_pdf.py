import PyPDF2

try:
    with open('FEEDBACK CALCULADORA.pdf', 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        text = []
        for i, page in enumerate(reader.pages):
            text.append(f"--- PAGE {i+1} ---")
            text.append(page.extract_text())
        
        with open('feedback_extracted.txt', 'w', encoding='utf-8') as out:
            out.write('\n'.join(text))
    print("Extracted successfully.")
except Exception as e:
    import traceback
    traceback.print_exc()
