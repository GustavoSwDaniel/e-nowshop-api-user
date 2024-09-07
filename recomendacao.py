from sqlalchemy import create_engine
import pandas as pd
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules

# Conectar ao banco de dados PostgreSQL
engine = create_engine('postgresql+psycopg2://postgres:t8ltavvRLd@127.0.0.1:5432/postgres')

# Carregar os dados das tabelas orders e order_items
query = """
SELECT oi.order_id, oi.product_id, o.user_id
FROM order_items oi
JOIN orders o ON oi.order_id = o.id
"""
df = pd.read_sql(query, engine)

# Criar uma tabela de pivot para ter pedidos em linhas e produtos em colunas
order_product_matrix = df.pivot_table(index='order_id', columns='product_id', aggfunc='size', fill_value=0)

# Mostrar a matriz de co-ocorrência de produtos (opcional, apenas para visualização)
print(order_product_matrix.head())

order_product_matrix = order_product_matrix.applymap(lambda x: 1 if x > 0 else 0)


# Aplicar o algoritmo Apriori para encontrar itens frequentes
frequent_itemsets = apriori(order_product_matrix, min_support=0.01, use_colnames=True)

# Gerar regras de associação usando lift como métrica de interesse
rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1.0)

# Ordenar as regras por lift em ordem decrescente
rules = rules.sort_values(by=['lift'], ascending=False)

# Exibir as principais regras de associação
print(rules.head())


def recomendar_produtos(produto_comprado, rules, min_lift=1.0, num_recomendacoes=3):
    # Filtrar as regras para produtos associados ao produto comprado com lift mínimo
    filtered_rules = rules[(rules['antecedents'] == {produto_comprado}) & (rules['lift'] >= min_lift)]
    
    # Ordenar as regras por lift em ordem decrescente
    filtered_rules = filtered_rules.sort_values(by=['lift'], ascending=False).head(num_recomendacoes)
    
    # Extrair os produtos recomendados
    recommended_products = []
    for index, row in filtered_rules.iterrows():
        recommended_products.extend(list(row['consequents']))
    
    return recommended_products

# Exemplo de uso: recomendar produtos baseados no produto_id 1
while True:
    produto_comprado = int(input("Entre o id do produto"))
    if produto_comprado == 0:
         break
    recomendacoes = recomendar_produtos(produto_comprado, rules)

    # Mostrar as recomendações
    print(f"Recomendações para produtos similares ao produto {produto_comprado}:")
    print(recomendacoes)
