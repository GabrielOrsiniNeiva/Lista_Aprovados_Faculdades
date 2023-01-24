"""
Módulo responsável por gerar um CSV com a lista de aprovados da UFRJ, dado o PDF
disponiblizado pela própria universidade.

Author: gabrors
Date: 01/2023
"""

import os
import json
import tabula
import requests
import pandas as pd
from enum import Enum

class Universidade(Enum):
    UFMG = "UFMG"
    UFRJ = "UFRJ"
    UFF = "UFF"

class Chamada:
    def __init__(self, universidade:str, periodo:str, url:str):
        self.universidade = Universidade(universidade).value
        self.periodo = periodo
        self.url = url
        self.tabula = self.open_json()
        self.pdf_file = f'downloads/{self.universidade}_{self.periodo}.pdf'
        self.csv_file = f'output/{self.universidade}_{self.periodo}.csv'
        self.download_files()
        
    def download_files(self):
        """
        Executa o download do PDF pela url
        """
        # Faz o download se o arquivo não existe no diretório
        if not os.path.isfile(self.pdf_file):
            response = requests.get(self.url)
            file = open(self.pdf_file, "wb")
            file.write(response.content)
            file.close()
    
    def open_json(self):
        """
        Abre JSON de configuração extraído do Tabula
        """
        file_path = f'config/tabula-{self.universidade}_{self.periodo}.json'

        with open(file_path, 'r') as f:
            tabula = json.load(f)

        return tabula
       
    def _UFMG_converter(self):
        for i, spec in enumerate(self.tabula):
            
            # Defining area
            top = spec["y1"]
            left = spec["x1"]
            bottom = spec["y2"]
            right = spec["x2"]

            tb_area = [top, left, bottom, right]
            
            # Lendo tabela no PDF
            pdf_reader = tabula.read_pdf(
                self.pdf_file,
                area=tb_area,
                pages=spec["page"],
                encoding='utf-8'
            )

            name_col = pdf_reader[0].filter(regex=("(NOME|CANDIDATO)")).columns[0]
            
            # Algumas páginas os candidatos aparecem numa coluna Unnamed
            if pdf_reader[0][name_col].isna().any():
                if 'Unnamed: 0' in pdf_reader[0].columns:
                    pdf_reader[0].drop(name_col, axis=1, inplace=True)
                    pdf_reader[0].rename(columns={'Unnamed: 0': name_col}, inplace=True)
            
            # Cria o df se for primeira iteração
            if i == 0:
                df = pdf_reader[0].copy()
            else:
                df = df.append(pdf_reader[0])
            
        df.to_csv(self.csv_file, index=False, encoding='utf-8')
    
    def _UFRJ_converter(self):
        for i, spec in enumerate(self.tabula):
            
            # Defining area
            top = spec["y1"]
            left = spec["x1"]
            bottom = spec["y2"]
            right = spec["x2"]

            tb_area = [top, left, bottom, right]
            
            # Lendo tabela no PDF
            pdf_reader = tabula.read_pdf(
                self.pdf_file,
                area=tb_area,
                pages=spec["page"],
                encoding='utf-8'
            )
            
            name_col = pdf_reader[0].filter(regex=("(NOME|CANDIDATO)")).columns[0]
            
            # Algumas páginas os candidatos aparecem numa coluna Unnamed
            if pdf_reader[0][name_col].isna().any():
                if 'Unnamed: 0' in pdf_reader[0].columns:
                    pdf_reader[0].drop(name_col, axis=1, inplace=True)
                    pdf_reader[0].rename(columns={'Unnamed: 0': name_col}, inplace=True)
            
            # Cria o df se for primeira iteração
            if i == 0:
                df = pdf_reader[0].copy()
                
            else:
                df = df.append(pdf_reader[0])
            
        df.to_csv(self.csv_file, index=False, encoding='utf-8')

    def pdf_table_to_csv(self):
        """
        Função responsável por ler um PDF e transformar as tabelas presentes nele
        em um CSV.
        """
        
        if self.universidade == 'UFMG':
            return self._UFMG_converter()
        
        if self.universidade == 'UFRJ':
            return self._UFRJ_converter()


if __name__ == "__main__":
    with open('../config.json', 'r') as f:
        links = json.load(f)
    
    # Criando um objeto da nossa classe para cada lista de aprovados
    chamadas = []
    for facul in links:
        for lista in links[facul]:
            chamadas.append(
                Chamada(
                    facul,
                    lista,
                    links[facul][lista]
                )
            )

    # Convertendo a lista em CSV
    for c in chamadas:
        c.pdf_table_to_csv()