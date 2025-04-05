import pdfkit
import os

# Exemplo de caminho no Windows
caminho_executavel = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'

config = pdfkit.configuration(wkhtmltopdf=caminho_executavel)


def html_para_pdf(caminho_html, caminho_pdf):
    if not os.path.exists(caminho_html):
        raise FileNotFoundError(f"Arquivo HTML não encontrado: {caminho_html}")

    try:
        pdfkit.from_file(caminho_html, caminho_pdf, configuration=config)
        print(f"PDF gerado com sucesso: {caminho_pdf}")
    except Exception as e:
        print(f"Erro ao converter HTML para PDF: {e}")


# Exemplo de uso
html_para_pdf("template/boss-br.html", "template.pdf")
