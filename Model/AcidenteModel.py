import sqlite3
import pandas as pd
import os

class AcidenteModel:
    def __init__(self, db_path):
       
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

        self.conn = sqlite3.connect(db_path)
        self.create_table()


    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS acidentes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_inversa TEXT,
            dia_semana TEXT,
            horario TEXT,
            uf TEXT,
            br TEXT,
            km TEXT,
            municipio TEXT,
            causa_acidente TEXT,
            tipo_acidente TEXT,
            classificacao_acidente TEXT,
            fase_dia TEXT,
            sentido_via TEXT,
            condicao_metereologica TEXT,
            tipo_pista TEXT,
            tracado_via TEXT,
            uso_solo TEXT,
            pessoas INTEGER,
            mortos INTEGER,
            feridos_leves INTEGER,
            feridos_graves INTEGER,
            ilesos INTEGER,
            ignorados INTEGER,
            feridos INTEGER,
            veiculos INTEGER,
            latitude REAL,
            longitude REAL,
            regional TEXT,
            delegacia TEXT,
            uop TEXT
        );
        """
        self.conn.execute(query)
        self.conn.commit()

    def inserir_dados(self, df: pd.DataFrame):
        df.to_sql("acidentes", self.conn, if_exists="replace", index=False)


    def listar_acidentes(self):
        return pd.read_sql("SELECT * FROM acidentes", self.conn)

    def listar_por_uf(self, uf="PA"):
        query = f"SELECT * FROM acidentes WHERE uf = ?"
        return pd.read_sql(query, self.conn, params=(uf,))