import os
import re
import csv
from collections import defaultdict

# Definição dos grupos de tags
TAG_GROUPS = {
    "Resiliência e Boas Virtudes": ['18', '8', '15', '45'],
    "Política, Militares e Políticos": ['2', '13', '12'],
    "Luta de Classes e Questões Raciais": ['17', '20', '46'],
    "Desencorajamento de Crimes e Drogas": ['6', '19'],
    "Rap com instrumento social": ['3'],
    "Respeito e Valorização a mulher": ['25', '37'],
    "Criminalidade": ['41', '4', '35'],
    "Ego e Poder": ['22', '34', '30'],
    "Interesses Sexuais": ['26'],
    "Ostentação": ['32'],
    "Depreciação da mulher": ['29', '27', '40', '39'],
    "Alcool, cigarro e drogas": ['18', '5']
}


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

    # Agrupar tags e criar cabeçalhos ordenados
    group_headers = sorted(TAG_GROUPS.keys())

    # PRINT TO CONSOLE
    print("\n=== RESULTADOS ANALISADOS ===")
    header = ["Artist", "Song", "Total"] + group_headers
    col_widths = [
        max(len("Artist"), max(len(res['artist']) for res in all_results)),
        max(len("Song"), max(len(res['song']) for res in all_results)),
        max(len("Total"), len(str(max(res['total_sem_tags'] + res['total_nas_tags'] for res in all_results)))),
        *[max(len(header),
              len(str(max(sum(res['total_por_tag'].get(tag, 0) for tag in TAG_GROUPS[header]) for res in all_results))))
          for header in group_headers]
    ]

    # Print table header
    print("|".join(f"{h:^{w}}" for h, w in zip(header, col_widths)))
    print("-" * (sum(col_widths) + len(col_widths) - 1))

    # Print each row
    for res in all_results:
        total = res['total_sem_tags'] + res['total_nas_tags']
        row = [res['artist'], res['song'], str(total)]
        for group in group_headers:
            group_total = sum(res['total_por_tag'].get(tag, 0) for tag in TAG_GROUPS[group])
            row.append(str(group_total))
        print("|".join(f"{v:^{w}}" for v, w in zip(row, col_widths)))

    # EXPORT TO CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        for res in all_results:
            total = res['total_sem_tags'] + res['total_nas_tags']
            row = [res['artist'], res['song'], total]
            for group in group_headers:
                group_total = sum(res['total_por_tag'].get(tag, 0) for tag in TAG_GROUPS[group])
                row.append(group_total)
            writer.writerow(row)

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