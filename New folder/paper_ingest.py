import arxiv
import fitz  # PyMuPDF
import requests
import os
import tempfile

def fetch_arxiv_pdf(query, max_results=1):
    search = arxiv.Search(query=query, max_results=max_results)
    results = list(search.results())
    if not results:
        return None, None, None
    paper = results[0]
    pdf_url = paper.pdf_url
    title = paper.title
    # Download PDF to temp file
    response = requests.get(pdf_url)
    temp_dir = tempfile.gettempdir()
    safe_title = "".join([c if c.isalnum() else "_" for c in title])[:30]
    pdf_path = os.path.join(temp_dir, f"{safe_title}.pdf")
    with open(pdf_path, "wb") as f:
        f.write(response.content)
    return pdf_path, title, paper

def extract_text_from_pdf(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        text += page.get_text()
    return text