from pathlib import Path
import json


# BASE_DIR = …/API_orcamentos
BASE_DIR = Path(__file__).resolve().parents[2]
BD_DIR   = BASE_DIR / "bd"
FUNC_DIR = BD_DIR / "funcionarios"


def get_data(nome: str) -> dict:
    """
    Lê bd/funcionarios/{nome}.json e devolve um dicionário com os dados do funcionário.
    Levanta FileNotFoundError se o arquivo não existir.
    """
    path = FUNC_DIR / f"{nome}.json"
    with path.open(encoding="utf-8") as f:
        return json.load(f)