import os
import re
import csv
from collections import defaultdict


def analisar_arquivos_musicas(pasta="musicas", output_file="music_analysis.csv"):
    if not os.path.exists(pasta):
        print(f"A pasta '{pasta}' não foi encontrada.")
        return

    arquivos = [f for f in os.listdir(pasta) if f.endswith('.txt')]

    if not arquivos:
        print(f"Nenhum arquivo .txt encontrado na pasta '{pasta}'.")
        return

    # Process all files first
    all_results = []
    all_tags = set()

    for arquivo in arquivos:
        caminho = os.path.join(pasta, arquivo)
        with open(caminho, 'r', encoding='utf-8') as f:
            conteudo = f.read()

        resultado = processar_conteudo(conteudo)
        filename = arquivo[:-4]  # Remove .txt
        artist, song = (filename.split(' - ', 1) if ' - ' in filename else (filename, ''))
        resultado.update({'artist': artist, 'song': song, 'filename': filename})
        all_results.append(resultado)
        all_tags.update(resultado['total_por_tag'].keys())

    sorted_tags = sorted(all_tags, key=lambda x: int(x))

    # PRINT TO CONSOLE
    print("\n=== RESULTADOS ANALISADOS ===")
    header = ["Artist", "Song", "Total"] + sorted_tags
    col_widths = [
        max(len("Artist"), max(len(res['artist']) for res in all_results)),
        max(len("Song"), max(len(res['song']) for res in all_results)),
        max(len("Total"), len(str(max(res['total_sem_tags'] + res['total_nas_tags'] for res in all_results)))),
        *[max(len(tag), len(str(max(res['total_por_tag'].get(tag, 0) for res in all_results)))) for tag in sorted_tags]
    ]

    # Print table header
    print("|".join(f"{h:^{w}}" for h, w in zip(header, col_widths)))
    print("-" * (sum(col_widths) + len(col_widths) - 1))

    # Print each row
    for res in all_results:
        total = res['total_sem_tags'] + res['total_nas_tags']
        row = [res['artist'], res['song'], str(total)] + [str(res['total_por_tag'].get(tag, 0)) for tag in sorted_tags]
        print("|".join(f"{v:^{w}}" for v, w in zip(row, col_widths)))

    # EXPORT TO CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        for res in all_results:
            total = res['total_sem_tags'] + res['total_nas_tags']
            writer.writerow(
                [res['artist'], res['song'], total] + [res['total_por_tag'].get(tag, 0) for tag in sorted_tags])

    print(f"\n✅ Dados impressos acima E exportados para '{output_file}' (arquivo sobrescrito)")


def processar_conteudo(conteudo):
    padrao_tag = re.compile(r'<\d+>.*?</\d+>', re.DOTALL)
    caracteres_ignorados = r'\s,.;:!?()[]{}"\'´`^~...-–—/\\+*=<>|@#$%&_'

    conteudo_sem_tags = re.sub(r'<\d+>.*?</\d+>', '', conteudo, flags=re.DOTALL)
    total_sem_tags = sum(1 for char in conteudo_sem_tags if char not in caracteres_ignorados)

    total_por_tag = defaultdict(int)
    total_nas_tags = 0

    for tag_match in re.finditer(r'<(\d+)>(.*?)</\1>', conteudo, re.DOTALL):
        tag_num, tag_conteudo = tag_match.groups()
        contagem = sum(1 for char in tag_conteudo if char not in caracteres_ignorados)
        total_por_tag[tag_num] += contagem
        total_nas_tags += contagem

    return {
        'total_sem_tags': total_sem_tags,
        'total_nas_tags': total_nas_tags,
        'total_por_tag': dict(total_por_tag)
    }


if __name__ == "__main__":
    analisar_arquivos_musicas()