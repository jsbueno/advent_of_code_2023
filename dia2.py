cores = {"red": 12, "green": 13, "blue": 14}
aa = """Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green
Game 2: 1 blue, 2 green; 3 green, 4 blue, 1 red; 1 green, 1 blue
Game 3: 8 green, 6 blue, 20 red; 5 blue, 4 red, 13 green; 5 green, 1 red
Game 4: 1 green, 3 red, 6 blue; 3 green, 6 red; 3 green, 15 blue, 14 red
Game 5: 6 red, 1 blue, 3 green; 2 blue, 1 red, 2 green"""


bb  =aa.split("\n")
bb


def checa_jogo(linha):
    cabec, corpo = linha.split(":")
    id = int(cabec.split()[-1])
    rodadas  = corpo.split(";")
    maximo_rodadas = obtem_maximo(rodadas)
    for cor in cores:
        if cores[cor] < maximo_rodadas.get(cor, 0):
            return False
    return True

def obtem_maximo(rodadas):
    maximos = {}
    for rodada in rodadas:
        rodada = converter_rodada(rodada)
        for cor in cores:
            maximos[cor] = max(maximos.get(cor, 0), rodada.get(cor, 0))
    return rodadas

bb[0]
cc = bb[0].split(":")[1].split(";")
cc

def força_jogo(linha):
    cabec, corpo = linha.split(":")
    id = int(cabec.split()[-1])
    rodadas  = corpo.split(";")
    maximo_rodadas = obtem_maximo(rodadas)
    return math.prod(maximo_rodadas.values())


def converter_rodada(rodada):
    items = [cubos.strip() for cubos in rodada.split(",")]
    mapa = {}
    for item in items:
        quant, cor = item.split()
        mapa[cor] = int(quant)
    return mapa


#parte 1
sum(result for linha in bbb if (result:=checa_jogo(linha)) is not None)
#parte 2
sum(força_jogo(linha) for linha in bbb)
