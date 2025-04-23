import re
import os
from decimal import Decimal

def parse_price(price_str):
    """
    Converte uma string como "R$ 1.234,56" para Decimal('1234.56').
    """
    if not price_str:
        return Decimal("0")
    normalized = price_str.upper().replace("R$", "").strip().replace(".", "").replace(",", ".")
    try:
        return Decimal(normalized)
    except:
        return Decimal("0")

def format_price(value):
    """
    Converte Decimal(1234.56) para uma string "R$ 1.234,56"
    """
    int_part, frac_part = divmod(value, 1)
    int_part_str = f"{int(int_part):,}".replace(",", ".")
    cents = f"{int(round(frac_part * 100)):02d}"
    return f"R$ {int_part_str},{cents}"

def replace_all_placeholders(text, data_dict):
    """
    Substitui todos os {{ placeholders }} no HTML com os valores vindos do data_dict.
    """
    pattern = re.compile(r"{{\s*([^}]+?)\s*}}")
    def replacer(match):
        chave = match.group(1).strip()
        return str(data_dict.get(chave, ""))
    return pattern.sub(replacer, text)

def insert_br_after_underscores(html):
    """
    Adiciona <br><br> após sequências de 5 ou mais underscores.
    """
    pattern = re.compile(r'(_{5,})(?!<br>)')
    return pattern.sub(r'\1<br><br>', html)

def preencher_template(caminho_template_base, caminho_destino, dados):
    """
    Lê o template HTML, preenche os campos com base no dicionário `dados`,
    e salva o HTML preenchido no `caminho_destino`.
    """

    # 1. Carrega o HTML do template
    with open(caminho_template_base, "r", encoding="windows-1252") as f:
        html_base = f.read()

    # 2. Cálculo de subtotal do produto
    try:
        qtd = int(dados.get("qtdP", "0") or 0)
        valor_unitario = parse_price(dados.get("ValorP", "0"))
        subtotal = format_price(qtd * valor_unitario)
    except:
        subtotal = "R$ 0,00"

    # 3. Injeta subtotal no dicionário
    dados["subtotalP"] = subtotal

    # 4. Substitui todos os placeholders no HTML
    html_preenchido = replace_all_placeholders(html_base, dados)

    # 5. Adiciona quebras de linha onde necessário
    html_preenchido = insert_br_after_underscores(html_preenchido)

    # 6. Garante que a pasta de destino exista
    os.makedirs(os.path.dirname(caminho_destino), exist_ok=True)

    # 7. Salva o HTML final preenchido
    with open(caminho_destino, "w", encoding="utf-8") as f:
        f.write(html_preenchido)

    return caminho_destino
