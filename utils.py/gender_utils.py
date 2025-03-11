# gender_utils.py

def adjust_gender_ending(text: str, genero: str) -> str:
    """
    Ajusta o final de 'text' de acordo com o gênero informado.
    Espera que 'genero' seja:
      - "M" para Masculino (não altera o texto)
      - "F" para Feminino (troca "o" por "a" e "os" por "as")
      - "N" para Não-binário (troca "o" por "e" e "os" por "es")
    Se o texto não terminar em "o" ou "os", retorna o texto original.
    """
    genero = genero.strip().upper()  # garante que esteja em maiúsculas sem espaços

    SUBSTITUICOES = {
        "M": {"o": "o", "os": "os"},  # Mantém como está
        "F": {"o": "a", "os": "as"},
        "N": {"o": "e", "os": "es"}
    }

    if genero not in SUBSTITUICOES:
        return text

    if text.endswith("os"):
        return text[:-2] + SUBSTITUICOES[genero]["os"]
    elif text.endswith("o"):
        return text[:-1] + SUBSTITUICOES[genero]["o"]
    else:
        return text


def get_professional_title(professional_profile):
    """
    Retorna o nome do profissional com o título apropriado baseado no gênero.

    Fluxo:
        1. Obtém o `display_name` do profissional.
        2. Obtém o `genero` do profissional.
        3. Define o título adequado:
            - "Dra." para gênero "F"
            - "Drx." para gênero "N"
            - "Dr." para gênero "M" ou padrão
        4. Retorna a string formatada com título + nome.

    Args:
        professional_profile (dict): Dicionário contendo pelo menos "display_name" e "genero".

    Returns:
        str: Nome formatado com o título adequado (ex: "Dra. Estrela").
    """
    professional_name = professional_profile.get("display_name", "Profissional")
    gender_professional = professional_profile.get("genero", "M")  # Padrão é "M"

    if gender_professional == "F":
        titulo = "Dra."
    elif gender_professional == "N":
        titulo = "Drx."
    else:
        titulo = "Dr."

    return f"{titulo} {professional_name}"