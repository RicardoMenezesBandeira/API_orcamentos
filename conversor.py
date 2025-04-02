from weasyprint import HTML

# Converter o HTML para PDF
def convert(modelo,codigo):
    html = HTML(modelo)
    html.write_pdf(f"{codigo}_{modelo}.pdf")

    print("PDF gerado com sucesso: output.pdf")
