import os
import sqlite3
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

from src.utils import get_embedding


def get_data_from_db() -> pd.DataFrame:
    database_path = "data/mapbot Numero.db"
    conn = sqlite3.connect(database_path)
    query = "SELECT * FROM 'MAPBOT'"
    return pd.read_sql_query(query, conn)


def main():
    load_dotenv()
    api_key = os.getenv('OPEN_AI_API_KEY')
    client = OpenAI(api_key=api_key)

    embedding_model = "text-embedding-ada-002"

    df = get_data_from_db()
    df = df.dropna()

    df["embedding"] = df.topicText.apply(lambda x: get_embedding(client, x, model=embedding_model))

    df.to_csv("data/mapbot_with_embeddings.csv")


if __name__ == "__main__":
    main()
