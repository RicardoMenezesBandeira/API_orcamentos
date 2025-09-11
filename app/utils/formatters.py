import re
from babel.numbers import format_currency

from babel.numbers import format_decimal, format_currency

def parse_valor(valor_str: str) -> float:
    """
    Converte strings numéricas com vírgula ou ponto para float.
    Ex: "1234,56" -> 1234.56
        "1.234,56" -> 1234.56
        "1234.56" -> 1234.56
    """
    valor_str = valor_str.strip()

    if "," in valor_str and "." in valor_str:
        valor_str = valor_str.replace(".", "").replace(",", ".")
    elif "," in valor_str:
        valor_str = valor_str.replace(",", ".")
    return float(valor_str)


def formatar_dinheiro_brl(valor, casas: int = 4, incluir_simbolo: bool = True) -> str:
    """
    Formata número para BRL no padrão:
    xxx.xxx.xxx,xxxx
    """
    if isinstance(valor, str):
        valor = parse_valor(valor)

    pattern = "#,##0." + "0" * casas  # garante casas fixas

    if incluir_simbolo:
        return format_currency(valor, "BRL", locale="pt_BR", format="¤ " + pattern)
    else:
        return format_decimal(valor, locale="pt_BR", format=pattern)


def formatar_cnpj(cnpj: str) -> str:       # :contentReference[oaicite:6]{index=6}
    cnpj = re.sub(r"\D", "", cnpj)
    return re.sub(r"^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$", r"\1.\2.\3/\4-\5", cnpj)

def formatar_cpf(cpf: str) -> str:         # :contentReference[oaicite:7]{index=7}
    cpf = re.sub(r"\D", "", cpf)
    return re.sub(r"^(\d{3})(\d{3})(\d{3})(\d{2})$", r"\1.\2.\3-\4", cpf)
