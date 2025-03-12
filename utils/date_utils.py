from datetime import datetime


def format_date(iso_date):
    """
    Converte uma data ISO 8601 (YYYY-MM-DDTHH:MM:SS.ssssss) em dia, mês e ano.

    Fluxo:
        1. Verifica se a data não é vazia.
        2. Tenta extrair a parte da data (YYYY-MM-DD) ignorando a hora.
        3. Converte a string da data em um objeto `datetime`.
        4. Retorna o dia, mês e ano como inteiros.
        5. Se houver erro na conversão, retorna `(None, None, None)`.

    Args:
        iso_date (str): Data no formato ISO 8601.

    Returns:
        tuple: (dia, mês, ano) como inteiros ou (None, None, None) se a conversão falhar.

    Calls:
        Nenhuma chamada externa, apenas manipulação interna de datas.
    """
    if not iso_date:
        return None, None, None  # Retorna valores vazios se a data for inválida

    try:
        # 🗓️ Converte a data ignorando a hora (pega só YYYY-MM-DD)
        date_obj = datetime.strptime(iso_date.split("T")[0], "%Y-%m-%d")
        return date_obj.day, date_obj.month, date_obj.year
    except ValueError:
        return None, None, None  # Retorna valores vazios se o formato estiver errado
