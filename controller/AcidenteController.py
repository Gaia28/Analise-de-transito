import pandas as pd
import re
import os
import logging
from model.AcidenteModel import AcidenteModel


class AcidenteController:
    def __init__(self):
        pass

    def extrair_ano_do_nome(self, nome_arquivo):
        """Usa regex para encontrar um ano de 4 dígitos no nome do arquivo."""
        match = re.search(r'\d{4}', nome_arquivo)
        if match:
            return match.group(0)
        return None

    def processar_planilha(self, arquivo):
        try:
            ano = self.extrair_ano_do_nome(arquivo.name)
            if not ano:
                raise Exception(
                    f"Nome de arquivo inválido. O nome '{arquivo.name}' deve conter um ano com 4 dígitos.")

            db_path = f"data/acidentes_{ano}.db"
            model = AcidenteModel(db_path=db_path)

            if arquivo.name.endswith(".csv"):
                df = pd.read_csv(arquivo, encoding="latin1", sep=";")
            else:
                df = pd.read_excel(arquivo)

            df.columns = [re.sub(r"\s+", "_", str(c).strip().lower())
                          for c in df.columns]

            if "uf" not in df.columns:
                raise Exception(
                    f"A coluna 'uf' é obrigatória e não foi encontrada.")

            df_pa = df[df["uf"].str.upper() == "PA"]

            if not df_pa.empty:
                model.inserir_dados(df_pa)

            return df_pa, db_path

        except Exception as e:
            raise Exception(f"Erro ao processar a planilha: {e}")

    def listar_bancos_de_dados(self):
        data_dir = "data"
        if not os.path.exists(data_dir):
            return []
        files = [f for f in os.listdir(data_dir) if f.endswith(
            ".db") or f.endswith(".csv")]
        return sorted(files)

    def listar_dados_por_banco(self, nome_banco):
        db_path = f"data/{nome_banco}"

        if not os.path.exists(db_path):
            return pd.DataFrame()

        # Se for banco .db → usa o model normal
        if nome_banco.endswith(".db"):
            model = AcidenteModel(db_path)
            df = model.listar_por_uf("PA")
            return self._limpar_coordenadas(df)

        # Se for CSV → usa pandas direto
        if nome_banco.endswith(".csv"):
            try:
                # tenta primeiro separador ponto-e-vírgula, depois vírgula
                try:
                    df = pd.read_csv(db_path, sep=";", encoding="latin1")
                except Exception:
                    df = pd.read_csv(db_path, sep=",", encoding="latin1")

                # normaliza nomes de colunas
                df.columns = [re.sub(r"\s+", "_", str(c).strip().lower())
                              for c in df.columns]

                # garante presença de colunas numéricas chave com conversão segura
                def _to_int_series(series):
                    return pd.to_numeric(series.astype(str).str.replace(",", ".").str.replace(" ", ""), errors="coerce").fillna(0).astype(int)

                for num_col in ["mortos", "feridos", "feridos_graves", "veiculos", "pessoas"]:
                    if num_col in df.columns:
                        df[num_col] = _to_int_series(df[num_col])
                    else:
                        df[num_col] = 0

                # filtra somente PA se existir coluna uf
                if "uf" in df.columns:
                    df = df[df["uf"].str.upper() == "PA"]

                # limpeza de coordenadas após filtragem
                df = self._limpar_coordenadas(df)
                return df
            except Exception as e:
                logging.exception("Erro ao ler CSV '%s': %s", db_path, e)
                return pd.DataFrame()

        return pd.DataFrame()

    def _limpar_coordenadas(self, df):
        """Limpa e valida latitude/longitude do DataFrame"""

        def _clean_numeric_string(val):
            """Converte string com vírgula ou ponto em float válido"""
            if pd.isna(val) or val == "":
                return None
            s = str(val).strip()
            # substitui vírgula decimal por ponto
            s = s.replace(",", ".")
            # tenta encontrar o primeiro número float válido na string
            m = re.search(r'-?\d+\.\d+', s)
            if m:
                try:
                    return float(m.group(0))
                except:
                    return None
            # caso não encontre float com ponto, tenta inteiro
            m2 = re.search(r'-?\d+', s)
            if m2:
                try:
                    return float(m2.group(0))
                except:
                    return None
            return None

        # Procura colunas de coordenadas com nomes variados
        lat_cols = [c for c in df.columns if 'lat' in c.lower()]
        lon_cols = [c for c in df.columns if 'lon' in c.lower()
                    or 'long' in c.lower()]

        # Se encontrou colunas de latitude/longitude, limpa-as
        if lat_cols:
            for col in lat_cols:
                df[col] = df[col].apply(_clean_numeric_string)
                df = df[df[col].notna()]  # Remove linhas com lat inválida
                df = df[(df[col] >= -90) & (df[col] <= 90)]  # Valida range

        if lon_cols:
            for col in lon_cols:
                df[col] = df[col].apply(_clean_numeric_string)
                df = df[df[col].notna()]  # Remove linhas com lon inválida
                df = df[(df[col] >= -180) & (df[col] <= 180)]  # Valida range

        # Padroniza nomes para 'latitude' e 'longitude' se encontrou
        if lat_cols and lat_cols[0] not in ['latitude']:
            df.rename(columns={lat_cols[0]: 'latitude'}, inplace=True)
        if lon_cols and lon_cols[0] not in ['longitude']:
            df.rename(columns={lon_cols[0]: 'longitude'}, inplace=True)

        # Se tiver coluna "coords" com formato "-8.123,-49.456", extrai para lat/lon
        if "coords" in df.columns and ("latitude" not in df.columns or "longitude" not in df.columns):
            def _extract_lat_lon(s):
                if pd.isna(s) or s == "":
                    return (None, None)
                txt = str(s).replace(",", ".")
                parts = re.findall(r'-?\d+\.\d+', txt)
                if len(parts) >= 2:
                    lat = float(parts[0])
                    lon = float(parts[1])
                    if -90 <= lat <= 90 and -180 <= lon <= 180:
                        return (lat, lon)
                return (None, None)

            latitudes = []
            longitudes = []
            for s in df["coords"]:
                lat, lon = _extract_lat_lon(s)
                latitudes.append(lat)
                longitudes.append(lon)
            df["latitude"] = latitudes
            df["longitude"] = longitudes

            # Remove linhas com coords inválidas
            df = df[df["latitude"].notna() & df["longitude"].notna()]

        return df

    def get_dados_agrupados(self, df, coluna, top_n=10):
        if coluna not in df.columns:
            return pd.DataFrame()

        dados = df[coluna].value_counts().nlargest(top_n).reset_index()
        dados.columns = [coluna, 'total_acidentes']
        return dados

    def get_metricas_gerais(self, df):
        if df.empty:
            return {
                "total_acidentes": 0, "total_mortos": 0,
                "total_feridos_graves": 0, "total_veiculos": 0
            }

        metricas = {
            "total_acidentes": len(df),
            "total_mortos": df['mortos'].sum(),
            "total_feridos_graves": df['feridos_graves'].sum(),
            "total_veiculos": df['veiculos'].sum()
        }
        return metricas

    def listar_municipios(self, nome_banco):
        db_path = f"data/{nome_banco}"
        model = AcidenteModel(db_path)

        # Garantir que retornamos apenas municípios do Pará (uf = 'PA')
        query = "SELECT DISTINCT municipio FROM acidentes WHERE uf = 'PA' ORDER BY municipio ASC"
        df = pd.read_sql(query, model.conn)
        return df["municipio"].dropna().tolist()

    def dados_por_municipio(self, nome_banco, municipio):
        db_path = f"data/{nome_banco}"
        model = AcidenteModel(db_path)

        query = """
            SELECT 
                municipio,
                COUNT(*) AS total_acidentes,
                SUM(CASE WHEN feridos_graves IS NOT NULL THEN feridos_graves ELSE 0 END) AS total_feridos_graves,
                SUM(CASE WHEN mortos IS NOT NULL THEN mortos ELSE 0 END) AS total_mortos,
                SUM(CASE WHEN veiculos IS NOT NULL THEN veiculos ELSE 0 END) AS total_veiculos
            FROM acidentes
            WHERE uf = 'PA' AND municipio = ?
            GROUP BY municipio
        """

        return pd.read_sql(query, model.conn, params=(municipio,))
