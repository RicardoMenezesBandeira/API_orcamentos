import pdfkit
import os
from datetime import datetime

# Configurações - ajuste para seu sistema
WKHTMLTOPDF_PATH = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)

options = {
    'enable-local-file-access': None,
    'encoding': 'UTF-8',
    'page-size': 'A4',
    'margin-top': '5mm',
    'margin-right': '15mm',
    'margin-bottom': '0mm',
    'margin-left': '15mm',
    'dpi': 300,
    'disable-smart-shrinking': '',
    'no-outline': None,
    'print-media-type': '',
    'quiet': ''
}

def gerar_pdf(html_path, pdf_path):
    try:
        # Verificar se o arquivo HTML existe
        if not os.path.exists(html_path):
            raise FileNotFoundError(f"Arquivo HTML não encontrado: {html_path}")
        
        # Converter usando caminhos absolutos
        html_path = os.path.abspath(html_path)
        pdf_path = os.path.abspath(pdf_path)
        
        pdfkit.from_file(
            input=html_path,
            output_path=pdf_path,
            configuration=config,
            options=options
        )
        
        print(f"PDF gerado com sucesso em: {pdf_path}")
        return True
    
    except Exception as e:
        print(f"Erro ao gerar PDF: {str(e)}")
        return False

# Exemplo de uso
if __name__ == "__main__":
    # Caminhos (ajuste conforme sua estrutura de pastas)
    template_html = f"./template-PDF/modelo1.html"
    output_pdf = "orcamento_final.pdf"
    
    # Gerar PDF
    sucesso = gerar_pdf(template_html, output_pdf)
    
    if sucesso:
        print("Conversão concluída com sucesso!")
    else:
        print("Falha na conversão para PDF")