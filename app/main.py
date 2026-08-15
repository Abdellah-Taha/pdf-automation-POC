import pdfplumber, camelot, pytesseract
from PIL import Image

def extract_test():
    text = ""
    with pdfplumber.open("sample.pdf") as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

def extract_tables():
    tables = []
    with pdfplumber.open("sample.pdf") as pdf:
        for page in pdf.pages:
            tables.extend(page.extract_tables())
    return tables

def extract_images_to_text():
    text = ""
    with pdfplumber.open("sample.pdf") as pdf:
        for page in pdf.pages:
            for image in page.images:
                img = Image.open(image["path"])
                text += pytesseract.image_to_string(img)
    return text


def main():
    text = extract_test()
    print("Extracted Text:")
    print(text)

    tables = extract_tables()
    print("Extracted Tables:")
    for table in tables:
        print(table)

    image_text = extract_images_to_text()
    print("Extracted Text from Images:")
    print(image_text)
    
    
if __name__ == "__main__":
    main()
