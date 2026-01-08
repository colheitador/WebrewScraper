# importar pacotes importantes
from fastapi import FastAPI, HTTPException # para trabalhar com a API
import sqlite3 # banco de dados
import json # trabalhar com dicionários
import requests # parte de crawlear de novo
from bs4 import BeautifulSoup # parte de crawlear de novo
import datetime # registrar a data de crawleamento

# importar funções criadas em outro arquivo .py
from funcoes import func_todos_os_resultados, func_pesquisar_por_nome, func_pesquisar_por_preco_maximo,\
                    func_pesquisar_por_nome_e_preco, func_pesquisar_por_descricao, \
                    func_recriar_tabela, func_parsing, func_centralbrew, func_mariacervejeira, func_piquiribrewshop, \
                    func_deletar_centralbrew, func_deletar_mariacervejeira, func_deletar_piquiribrewshop, \
                    func_gerar_csv, func_csv_sem_resultados, criar_banco_usuario_temporario, verificar_tabela_no_banco #, deletar_banco_temporario


# nome para chamar o FastAPI
app = FastAPI()

## ''' IMPORTANTE: Para correta execução o terminal deve estar na pasta certa (C:\Users\denis\OneDrive\Documentos\tcc\codigos)'''


# ## conectar com o banco de dados
# con1 = sqlite3.connect("fermentos.db", check_same_thread=False) #isso aqui seria problemático se mais de um usuário estivesse usando, entao substituí essa função
# cursor1 = con1.cursor()
# abaixo está a função que permite criar um banco de dados temporário ao qual o usuário vai se conectar para não interferir na experiência de outros usuários
con1, cursor1, nome_banco = criar_banco_usuario_temporario()

# # Usando o evento shutdown do FastAPI para garantir que a função de limpeza seja chamada
# @app.on_event("shutdown")
# def shutdown():
#     print("Iniciando o processo de shutdown...")
#     # Deleta o banco temporário e fecha a conexão ao sair do app
#     deletar_banco_temporario(nome_banco, con1)
#     print(f"Conexão fechada e banco temporário '{nome_banco}' deletado.")

#------
# Redirecionar raiz "/" para "/docs"
from fastapi.responses import RedirectResponse

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")
#-----

#-----------------------------------------------------------------------------------------------------------------------------------------------------#
'''                                            FUNÇÕES PARA PESQUISAR NA BASE DE DADOS                                                                 '''              
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Função para gerar uma planilha e retornar o número de fermentos encontrados na base de dados
@app.get("/pesquisar/tudo")
def obter_numero_de_resultados_e_planilha_geral():
    return func_todos_os_resultados(cursor1)
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Função para pesquisar fermento por NOME
@app.get("/pesquisar/nome")
def pesquisar_por_nome(nome: str):
    return func_pesquisar_por_nome(nome, cursor1)
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Função para pesquisar fermento por PREÇO
@app.get("/pesquisar/preco")
def pesquisar_por_preco_maximo(preco_maximo: str): ## não é preciso converter o preço para float aqui, pois o valor deve estar como string pra funcionar na busca por f string dentro da função
    return func_pesquisar_por_preco_maximo(preco_maximo, cursor1)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Função para pesquisar fermento por NOME & PREÇO
@app.get("/pesquisar/nome_e_preco")
def pesquisar_por_nome_e_preco(nome: str, preco_maximo: str):
    return func_pesquisar_por_nome_e_preco(nome, preco_maximo, cursor1)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Função para pesquisar fermento por DESCRIÇÃO
@app.get("/pesquisar/descricao")
def pesquisar_por_descricao(descricao: str):
    return func_pesquisar_por_descricao(descricao, cursor1)
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#



#-----------------------------------------------------------------------------------------------------------------------------------------------------#
'''                                              FUNÇÃO PARA RECRIAR A TABELA                                                                      '''              
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
# Função para apagar a tabela atual e recriar do zero
@app.put("/recriar")
def recriar_tabela_do_zero():
    func_recriar_tabela(con1, cursor1)
    return "Tabela recriada (sem os dados que tinha anteriormente)"
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------------------------------------------------------------------------#




#-----------------------------------------------------------------------------------------------------------------------------------------------------#
'''                                              FUNÇÕES PARA REFAZER O WEB SCRAPING                                                                '''              
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
# Função para fazer o web scraping em https://centralbrew.com.br/fermentos
@app.post("/web_scraping/centralbrew")
def web_scraping_em_centralbrew():
    cb = func_centralbrew(con1, cursor1)
    # return "Foram obtidas as informações dos fermentos disponíveis em centralbrew.com.br"
    return cb # Foram obtidas as informações de X fermentos disponíveis no website centralbew
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
# Função para fazer o web scraping em https://www.mariacervejeira.com.br/fermentos
@app.post("/web_scraping/mariacervejeira")
def web_scraping_em_mariacervejeira():
    mc = func_mariacervejeira(con1, cursor1)
    # return "Foram obtidas as informações dos fermentos disponíveis em mariacervejeira.com.br"
    return mc # Foram obtidas as informações de X fermentos disponíveis no website mariacervejeira
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
# Função para fazer o web scraping em https://www.piquiribrewshop.com.br/fermentos
@app.post("/web_scraping/piquiribrewshop")
def web_scraping_em_piquiribrewshop():
    pbs = func_piquiribrewshop(con1, cursor1)
    # return "Foram obtidas as informações dos fermentos disponíveis em piquiribrewshop.com.br"
    return pbs # Foram obtidas as informações de X fermentos disponíveis no website piquiribrewshop
#-----------------------------------------------------------------------------------------------------------------------------------------------------#




#-----------------------------------------------------------------------------------------------------------------------------------------------------#
'''                                                         FUNÇÕES PARA DELETAR                                                            '''               
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
# Função para DELETAR os resultados provenientes do fornecedor centralbrew"
@app.delete("/deletar/centralbrew")
def deletar_centralbrew():
    return func_deletar_centralbrew(con1, cursor1)
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
# Função para DELETAR os resultados provenientes do fornecedor mariacervejeira"
@app.delete("/deletar/mariacervejeira")
def deletar_mariacervejeira():
    return func_deletar_mariacervejeira(con1, cursor1)
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
# Função para DELETAR os resultados provenientes do fornecedor piquiribrewshop"
@app.delete("/deletar/piquiribrewshop")
def deletar_piquiribrewshop():
    return func_deletar_piquiribrewshop(con1, cursor1)
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
