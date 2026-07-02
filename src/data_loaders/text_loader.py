import pdb
import argparse
from pathlib import Path
from pypdf import PdfReader

def load_file(filename: str = "", verbose = True) -> dict:
    if not filename:
        print(f"Filename cannot be empty.")
    elif not Path(filename).is_file():
        print("The file does not exist.")
    else:
        content = {'source': 'text', 'filename': filename, 'content', [], 'pages': None}
        ext = Path(filename).suffix

        # Read normal txt file
        if 'txt' == ext:
            with open(filename, "r", encoding="utf-8") as file:
                content['content'].append(file.read())
                content['pages'] = 1

        # Read pdf file
        elif 'pdf' == ext:
            reader = PdfReader("document.pdf")
            total_pages = len(reader.pages)
            if not reader.pages:
                print(f"Failure to read PDF content.")
            for index, page in enumerate(reader.pages):
                content['content'].append(page.extract_text())
            content['pages'] = index
        return content

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Text File Loader.')
    parser.add_argument('-f', '--file', required=True, help='Full path filename to load.')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output.')

    args = parser.parse_args()

    # Extract content dictionary
    content = load_file(verbose = args.verbose)
    pdf.set_trace()