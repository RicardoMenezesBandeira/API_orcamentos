from pdf2docx import Converter

# Caminhos de entrada e saída
input_pdf = "pdfs_iniciais/Orcamento_3826_PETROLEO_BRASILEIRO_S_A_PETROBRAS (1).pdf"
output_docx = "orçamentos_docx/proposta_Petroleo_Brasileiro_convertida.docx"

# Inicializa o conversor e realiza a conversão
cv = Converter(input_pdf)
cv.convert(output_docx, start=0, end=None)  # Pode ajustar o intervalo de páginas se quiser
cv.close()

print(f"✅ Conversão concluída com sucesso: {output_docx}")
