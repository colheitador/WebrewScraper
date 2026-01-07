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
                    func_gerar_csv, func_csv_sem_resultados


# nome para chamar o FastAPI
app = FastAPI()

## ''' IMPORTANTE: Para correta execução o terminal deve estar na pasta certa (C:\Users\denis\OneDrive\Documentos\tcc\codigos)'''


## conectar com o banco de dados
con1 = sqlite3.connect("fermentos.db", check_same_thread=False)
cursor1 = con1.cursor()

#------
# Redirecionar raiz "/" para "/docs"
from fastapi.responses import RedirectResponse

@app.get("/")
def root():
    return RedirectResponse(url="/docs")
#-----


#-----------------------------------------------------------------------------------------------------------------------------------------------------#
'''                                            FUNÇÕES PARA PESQUISAR NA BASE DE DADOS                                                                 '''              
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Função para gerar uma planilha e retornar o número de fermentos encontrados na base de dados
@app.get("/pesquisar/tudo")
def obter_numero_de_resultados_e_planilha_geral():
    return func_todos_os_resultados()
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Função para pesquisar fermento por NOME
@app.get("/pesquisar/nome")
def pesquisar_por_nome(nome: str):
    return func_pesquisar_por_nome(nome)
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Função para pesquisar fermento por PREÇO
@app.get("/pesquisar/preco")
def pesquisar_por_preco_maximo(preco_maximo: str): ## não é preciso converter o preço para float aqui, pois o valor deve estar como string pra funcionar na busca por f string dentro da função
    return func_pesquisar_por_preco_maximo(preco_maximo)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Função para pesquisar fermento por NOME & PREÇO
@app.get("/pesquisar/nome_e_preco")
def pesquisar_por_nome_e_preco(nome: str, preco_maximo: str):
	return func_pesquisar_por_nome_e_preco(nome, preco_maximo)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# Função para pesquisar fermento por DESCRIÇÃO
@app.get("/pesquisar/descricao")
def pesquisar_por_descricao(descricao: str):
    return func_pesquisar_por_descricao(descricao)
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#



#-----------------------------------------------------------------------------------------------------------------------------------------------------#
'''                                              FUNÇÃO PARA RECRIAR A TABELA                                                                      '''              
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
# Função para apagar a tabela atual e recriar do zero
@app.put("/recriar")
def recriar_tabela_do_zero():
    func_recriar_tabela()
    return "Tabela recriada (sem os dados que tinha anteriormente)"
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------------------------------------------------------------------------#




#-----------------------------------------------------------------------------------------------------------------------------------------------------#
'''                                              FUNÇÕES PARA REFAZER O WEB SCRAPING                                                                '''              
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
# Função para fazer o web scraping em https://centralbrew.com.br/fermentos
@app.post("/web_scraping/centralbrew")
def web_scraping_em_centralbrew():
    cb = func_centralbrew()
    # return "Foram obtidas as informações dos fermentos disponíveis em centralbrew.com.br"
    return cb # Foram obtidas as informações de X fermentos disponíveis no website centralbew
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
# Função para fazer o web scraping em https://www.mariacervejeira.com.br/fermentos
@app.post("/web_scraping/mariacervejeira")
def web_scraping_em_mariacervejeira():
    mc = func_mariacervejeira()
    # return "Foram obtidas as informações dos fermentos disponíveis em mariacervejeira.com.br"
    return mc # Foram obtidas as informações de X fermentos disponíveis no website mariacervejeira
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
# Função para fazer o web scraping em https://www.piquiribrewshop.com.br/fermentos
@app.post("/web_scraping/piquiribrewshop")
def web_scraping_em_piquiribrewshop():
    pbs = func_piquiribrewshop()
    # return "Foram obtidas as informações dos fermentos disponíveis em piquiribrewshop.com.br"
    return pbs # Foram obtidas as informações de X fermentos disponíveis no website piquiribrewshop
#-----------------------------------------------------------------------------------------------------------------------------------------------------#




#-----------------------------------------------------------------------------------------------------------------------------------------------------#
'''                                                         FUNÇÕES PARA DELETAR                                                            '''               
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
# Função para DELETAR os resultados provenientes do fornecedor centralbrew"
@app.delete("/deletar/centralbrew")
def deletar_centralbrew():
    return func_deletar_centralbrew()
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
# Função para DELETAR os resultados provenientes do fornecedor mariacervejeira"
@app.delete("/deletar/mariacervejeira")
def deletar_mariacervejeira():
    return func_deletar_mariacervejeira()
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
# Função para DELETAR os resultados provenientes do fornecedor piquiribrewshop"
@app.delete("/deletar/piquiribrewshop")
def deletar_piquiribrewshop():
    return func_deletar_piquiribrewshop()
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------------------------------------------------------------------------#

