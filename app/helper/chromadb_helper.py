import chromadb
from chromadb.utils import embedding_functions

from app.settings import OPENAI_API_KEY

PERSIST_DIRECTORY = "chroma_db"


class ChromaDBService:
    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)
        self.collection = self.chroma_client.get_or_create_collection(
            name="room_embeddings",
            embedding_function=embedding_functions.OpenAIEmbeddingFunction(
                api_key=OPENAI_API_KEY, model_name="text-embedding-3-small"
            ),
        )

    def query_similar_rooms(self, query: str, n_results: int = 5):
        """
        Tool to search for lodges and villas based on user query using ChromaDB.
        """
        try:
            results = self.collection.query(query_texts=query, n_results=n_results)

            # Transform the results into the expected format
            rooms = []
            for doc, metadata, distance in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
                strict=True,
            ):
                room = {
                    "title": metadata.get('title', 'Unknown'),
                    "type": "lodge" if "lodge" in doc.lower() else "villa",
                    "description": doc,
                    "price": metadata.get('min_price', 'Unknown'),
                    "city": metadata.get('city', 'Unknown'),
                    "rating": metadata.get('rating', 'Unknown'),
                    "reviews_count": metadata.get('reviews_count', 'Unknown'),
                    "image_url": metadata.get('image_url', 'Unknown'),
                    "web_url": 'https://jajiga.com' + metadata.get('url', 'Unknown'),
                    "similarity_score": 1 - distance  # Convert distance to similarity score
                }
                rooms.append(room)
            return rooms
        except Exception as e:
            print(f"Error querying ChromaDB: {e}")
            return []


chroma_db_service = ChromaDBService()
