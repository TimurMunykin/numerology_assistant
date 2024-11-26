import pandas as pd
import numpy as np
from ast import literal_eval
from openai import OpenAI

from src.utils import get_embedding, cosine_similarity


def get_answer(question: str, api_key: str, answers_count: int = 50):
    client = OpenAI(api_key=api_key)

    datafile_path = "data/mapbot_with_embeddings.csv"

    df = pd.read_csv(datafile_path, encoding='utf-8')
    df["embedding"] = df.embedding.apply(literal_eval).apply(np.array)

    def search_reviews(df, product_description, n=3, pprint=False):
        product_embedding = get_embedding(
            client,
            product_description,
            model="text-embedding-ada-002"
        )
        df["similarity"] = df[df.topicNotes.notnull()].embedding.apply(
            lambda x: cosine_similarity(x, product_embedding)
        )

        results = df.sort_values("similarity", ascending=False).head(n)
        if pprint:
            for r in results.topicText:
                print(r[:200])
                print()
        return results

    results = search_reviews(df, question, n=answers_count)

    return results
