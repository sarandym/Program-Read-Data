from fpdf import FPDF
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

arquivo = r'C:/Users/Matheus Sarandy/Desktop/code/dados.csv'

def classificar_descricao(descricao):
    descricao = str(descricao).lower()
    
    categorias = {
        'Alimentação': ['alimento', 'comida', 'restaurante', 'cafe', 'padaria', 'mercado', 'Supermercado', 'pizza'],
        'Transporte': ['uber', 'taxi', 'ônibus', 'gasolina', 'combustível', 'transporte', 'carro'],
        'Moradia': ['aluguel', 'agua', 'luz', 'eletricidade', 'internet', 'telefone', 'condomínio'],
        'Saúde': ['farmácia', 'médico', 'hospital', 'remédio', 'consulta', 'saúde', 'academia'],
        'Educação': ['curso', 'escola', 'livro', 'educação', 'aula', 'formação'],
        'Lazer': ['cinema', 'jogo', 'entretenimento', 'viagem', 'lazer', 'diversão'],
        'Compras': ['loja', 'shopping', 'compra', 'vestuário', 'roupa', 'sapato', 'amazon', 'celular']
    }
    
    for categoria, palavras_chave in categorias.items():
        for palavra in palavras_chave:
            if palavra in descricao:
                return categoria
    
    return 'Outros'


def valor_total(valores):
    return valores.sum()

def total_por_categoria(df):
    return df.groupby ('categoria')['valor'].sum().to_dict()


df = pd.read_csv(arquivo, sep=';')


# auto detect the first text column (without knowing the name)
coluna_texto = df.columns[1]  # ajusta o índice para pegar a coluna correta

print("Usando coluna:", coluna_texto)

# apply the function
df['categoria'] = df[coluna_texto].apply(classificar_descricao)


print(df)
print('-' * 40)

print(f"Valor total: R$ {valor_total(df['valor']):.2f}")        #total = df.iloc[0:30, 2].sum()
                                                                #print(f"Valor total: R$ {total:.2f}")


print(f"Total por categoria:")
for categoria, total in total_por_categoria(df).items():
    print(f"  {categoria}: R$ {total:.2f}")

print('-' * 40)

limites = {
    'Alimentação': 0.30,
    'Transporte': 0.15,
    'Moradia': 0.25,
    'Saúde': 0.10,
    'Educação': 0.10,
    'Lazer': 0.05,
    'Compras': 0.05,
    'Outros': 0.05
}

def percentual_por_categoria(df):
    total = df['valor'].sum()
    return (df.groupby('categoria')['valor'].sum() / total).to_dict()

def analisar_gastos(percentuais, limites):
    analise = {}

    for categoria in limites.keys():
        perc = percentuais.get(categoria, 0)
        limite = limites[categoria]

        if perc > limite:
            analise[categoria] = f"Excedeu ({perc:.0%} > {limite:.0%}) - corte gastos"
        elif perc > limite * 0.8:
            analise[categoria] = f"Atencao ({perc:.0%} ~ {limite:.0%}) - perto do limite"
        else:
            analise[categoria] = f"Controlado ({perc:.0%} <= {limite:.0%})"

    return analise

def formatar_analise_gastos(analise):
    return "\n".join(f"{categoria}: {resultado}" for categoria, resultado in analise.items())

percentuais = percentual_por_categoria(df)
analise = analisar_gastos(percentuais, limites)

print("Análise de gastos por categoria:")
print(formatar_analise_gastos(analise))
print('-' * 40)

# Graph showing expenses by category
totais = total_por_categoria(df)
categorias = list(totais.keys())
valores = list(totais.values())

plt.figure(figsize=(10, 6))
sns.barplot(x=categorias, y=valores, palette='viridis')
plt.xticks(rotation=45)
plt.xlabel('Categoria')
plt.ylabel('Valor Total (R$)')
plt.title('Total de Gastos por Categoria')
plt.tight_layout()
plt.savefig(r'C:\Users\Matheus Sarandy\Desktop\grafico_categorias.png')
plt.show()

# Graph showing daily expenses in April
df['data'] = pd.to_datetime(df[df.columns[0]], format='%d/%m/%Y')
abril_df = df[df['data'].dt.month == 4]
gastos_diarios = abril_df.groupby(abril_df['data'].dt.day)['valor'].sum()

plt.figure(figsize=(10, 6))
plt.plot(gastos_diarios.index, gastos_diarios.values, marker='o')
plt.xlabel('Dia do Mês')
plt.ylabel('Valor Gasto (R$)')
plt.title('Gastos Diários em Abril')
plt.grid(True)
plt.tight_layout()
plt.savefig(r'C:\Users\Matheus Sarandy\Desktop\grafico_gastos_diarios_abril.png')
for dia, valor in zip(gastos_diarios.index, gastos_diarios.values):
    plt.text(dia, valor, f'{valor:.2f}', ha='center', va='bottom')
plt.show()

# Graph comparing percentage of spending by category vs limits
plt.figure(figsize=(10, 6))
categories = list(limites.keys())
perc_values = [percentuais.get(cat, 0) for cat in categories]
limit_values = [limites[cat] for cat in categories]
colors = ['red' if p > l else 'green' for p, l in zip(perc_values, limit_values)]
plt.bar(categories, perc_values, color=colors)
plt.plot(categories, limit_values, 'k--', label='Limite')
plt.xticks(rotation=45)
plt.ylabel('Porcentagem')
plt.title('Porcentagem de Gastos por Categoria vs Limites')
plt.legend()
plt.tight_layout()
plt.savefig(r'C:\Users\Matheus Sarandy\Desktop\grafico_porcentagem_limites.png')
plt.show()



# PDF GERENATION


def gerar_pdf(df, totais, percentuais, analise):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # page 1- Data CSV
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Relatorio de Gastos', ln=True, align='C')
    pdf.ln(4)

    # Title of columns
    colunas_csv = list(df.columns)
    pdf.set_font('Arial', 'B', 9)
    larguras = [38, 70, 25, 30, 30]  # ajuste conforme número de colunas
    for i, col in enumerate(colunas_csv):
        w = larguras[i] if i < len(larguras) else 30
        pdf.cell(w, 8, str(col), border=1, align='C')
    pdf.ln()

    # Line of data
    pdf.set_font('Arial', '', 8)
    for _, row in df.iterrows():
        for i, val in enumerate(row):
            w = larguras[i] if i < len(larguras) else 30
            texto = str(val) if not isinstance(val, float) else f'{val:.2f}'
            pdf.cell(w, 7, texto[:35], border=1)
        pdf.ln()

    # page 2: totals and percentages
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Resumo Financeiro', ln=True, align='C')
    pdf.ln(4)

    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, f'Valor Total Gasto: R$ {df["valor"].sum():.2f}', ln=True)
    pdf.ln(4)

    # Table: category | total | percentage | analysis
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(45, 8, 'Categoria', border=1, align='C')
    pdf.cell(35, 8, 'Total (R$)', border=1, align='C')
    pdf.cell(30, 8, 'Percentual', border=1, align='C')
    pdf.cell(75, 8, 'Analise', border=1, align='C')
    pdf.ln()

    pdf.set_font('Arial', '', 9)
    for cat in limites.keys():
        total_cat = totais.get(cat, 0)
        perc = percentuais.get(cat, 0)
        resultado = analise.get(cat, '-')
        pdf.cell(45, 7, cat, border=1)
        pdf.cell(35, 7, f'R$ {total_cat:.2f}', border=1, align='R')
        pdf.cell(30, 7, f'{perc:.1%}', border=1, align='C')
        pdf.cell(75, 7, resultado[:45], border=1)
        pdf.ln()

    # page 3: charts
    graficos = [
        (r'C:\Users\Matheus Sarandy\Desktop\grafico_categorias.png',         'Gastos por Categoria'),
        (r'C:\Users\Matheus Sarandy\Desktop\grafico_gastos_diarios_abril.png','Gastos Diarios em Abril'),
        (r'C:\Users\Matheus Sarandy\Desktop\grafico_porcentagem_limites.png', 'Percentual vs Limites'),
    ]

    for caminho, titulo in graficos:
        pdf.add_page()
        pdf.set_font('Arial', 'B', 13)
        pdf.cell(0, 10, titulo, ln=True, align='C')
        pdf.ln(2)
        pdf.image(caminho, x=10, w=190)

    saida = r'C:\Users\Matheus Sarandy\Desktop\relatorio_gastos.pdf'
    pdf.output(saida)
    print(f'PDF gerado em: {saida}')


gerar_pdf(df, totais, percentuais, analise)