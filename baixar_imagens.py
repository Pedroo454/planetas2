#!/usr/bin/env python3
"""Baixa as fotos do Hubble (usadas no index.html) para a pasta "images/".

Por que isso existe: a NASA tirou do ar o endereço original das fotos. O site já
funciona buscando cópias no Internet Archive, mas o ideal para a feira é ter as
fotos no seu próprio site (mais rápido e sem depender de terceiros).

Como usar (precisa do Python 3, sem instalar nada):
  1. Coloque este arquivo na MESMA pasta do index.html.
  2. Abra o terminal nessa pasta e rode:   python3 baixar_imagens.py
     (no Windows pode ser:                  py baixar_imagens.py)
  3. Aguarde (são ~350 fotos; leva alguns minutos). Pode interromper e rodar de
     novo: o que já foi baixado é pulado.
  4. Suba a pasta "images/" junto com o index.html no seu site.

Teste rápido, sem baixar nada:   python3 baixar_imagens.py --teste
"""
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

PASTA = Path(__file__).resolve().parent
HTML = PASTA / "index.html"
DESTINO = PASTA / "images"
ORIGEM = "https://imagine.gsfc.nasa.gov/hst_bday/images/"
# "im_" pede ao Wayback o arquivo cru da imagem; 2021 = foto mais próxima dessa época
ARCHIVE = "https://web.archive.org/web/2021im_/" + ORIGEM
PAUSA = 1.0       # segundos entre fotos (educado com o servidor do Internet Archive)
TENTATIVAS = 4


def nomes_das_fotos():
    """Lê do próprio index.html os nomes de arquivo (ex.: january-1-2019-galaxy-leo-iv.jpg)."""
    if not HTML.exists():
        sys.exit(f"Não achei o index.html em {PASTA}. Coloque este script na mesma pasta dele.")
    texto = HTML.read_text(encoding="utf-8")
    achados = re.findall(r'\["([a-z0-9][a-z0-9.\-]*\.(?:jpg|jpeg|png))"', texto)
    return sorted(set(achados))


def baixar(nome):
    url = ARCHIVE + nome
    ultimo_erro = "desconhecido"
    for tentativa in range(1, TENTATIVAS + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Planetario-Escolar)"})
            with urllib.request.urlopen(req, timeout=60) as r:
                tipo = r.headers.get("Content-Type", "")
                dados = r.read()
            if not tipo.startswith("image/") or len(dados) < 2000:
                return False, f"resposta não é uma imagem ({tipo or 'sem tipo'}, {len(dados)} bytes)"
            (DESTINO / nome).write_bytes(dados)
            return True, f"{len(dados) // 1024} KB"
        except urllib.error.HTTPError as e:
            ultimo_erro = f"HTTP {e.code}"
            if e.code == 404:
                break  # não existe no arquivo: não adianta repetir
        except Exception as e:  # rede instável, timeout etc.
            ultimo_erro = f"{type(e).__name__}: {e}"
        time.sleep(2 * tentativa)
    return False, ultimo_erro


def main():
    nomes = nomes_das_fotos()
    if "--teste" in sys.argv:
        print(f"{len(nomes)} fotos encontradas no index.html. Exemplo de endereço:")
        print("  " + ARCHIVE + nomes[0])
        print(f"Pasta de destino: {DESTINO}")
        return

    DESTINO.mkdir(exist_ok=True)
    falhas, novas, puladas = [], 0, 0
    for i, nome in enumerate(nomes, 1):
        if (DESTINO / nome).exists() and (DESTINO / nome).stat().st_size > 2000:
            puladas += 1
            continue
        ok, info = baixar(nome)
        print(f"[{i:>3}/{len(nomes)}] {'OK   ' if ok else 'FALHOU'} {nome}  ({info})", flush=True)
        if ok:
            novas += 1
        else:
            falhas.append(nome)
        time.sleep(PAUSA)

    print(f"\nPronto: {novas} baixadas agora, {puladas} já existiam, {len(falhas)} com falha.")
    if falhas:
        print("Fotos que falharam (rode o script de novo para tentar outra vez):")
        for n in falhas:
            print("  -", n)
        print("Enquanto isso, o site continua mostrando essas pelo Internet Archive.")
    print(f"As fotos estão em: {DESTINO}\nSuba essa pasta 'images' junto com o index.html.")


if __name__ == "__main__":
    main()baixar_imagens.py
