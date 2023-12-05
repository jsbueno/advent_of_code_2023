def checa_linha(linha):
    cabecalho, corpo = linha.split(" | ")
    vencedores = {int(num) for num in cabecalho.split(": ")[1].split(" ") if num}
    numeros = {int(num) for num in corpo.split() if num}
    return vencedores.intersection(numeros)


def calcula_vencedores(linha):
    vencedores = checa_linha(linha)
    if not vencedores:
        return 0
    return 2 ** (len(vencedores) - 1)

# parte 2

def duplica_cartoes(cartoes):
    cartoes_processados = 0
    copias = {} # {0: 1}
    for i, cartao in enumerate(cartoes):

        copias[i] = copias.get(i, 0) + 1
        vencedores = checa_linha(cartao)
        for j in range(len(vencedores)):
            if i + j + 1 >= len(cartoes):
                break
            copias[i + j + 1] = copias.get(i + j + 1, 0) + copias[i]
    return sum(copias.values())
