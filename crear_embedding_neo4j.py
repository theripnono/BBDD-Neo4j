"""
Pequeño scrip para crear los embeddings y meterlos en el nodo de neo4j
"""

from neo4j import GraphDatabase
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from dotenv import dotenv_values
import pandas as pd
import csv

config = dotenv_values(".env")
apikey = config['OPENAI_API_KEY']
llm = ChatOpenAI(openai_api_key=apikey)


#dimension por defecto 1536 al text-embedding-3-large
embeddings = OpenAIEmbeddings(model="text-embedding-3-large",
                              dimensions=1536,
                               openai_api_key=apikey)

# meter dentro del atributo correspondiente (receta_nombre) el embedding generado
text_embeddings = embeddings.embed_query("Bacalao")

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "adminadmin")

#Crear el embedding

def add_emb2Node(session:object, text_embeddings:str)-> object:
    
    """
    Insert a text embedding into a node
    """
    query = session.run("""
            MATCH (r:Receta)
            SET r.embedding = $text_embeddings
            RETURN r.receta_nombre, r.embedding
            """, {'text_embeddings': text_embeddings})
    query_df = query.to_df()
    
    return query_df
   
def get_all_nodes(session: object)-> object:
    
    """
    Get all nodes from the graph
    """
    result = session.run("""
                MATCH (r:Receta)
                RETURN r.receta_nombre, r.embedding
                         """)
    df =  result.to_df()
    return df

def get_similar_vector(session:object, text_embeddings:str)-> object:

    """
    Get similar nodes to a given text embedding
    """

    vector_search =session.run(""" 
                    MATCH (r:Receta)
                    WITH r, vector.similarity.cosine($query, r.embedding) AS score
                    RETURN r.receta_nombre, score
                    ORDER BY score DESCENDING
                    LIMIT 2;""",{ 'query': text_embeddings})
                               
    df =  vector_search.to_df()
    return df

def get_similar_nodes(session:object, text_embeddings:str)-> object:
    
    """
    Get similar nodes to a given text embedding
    """


    vector_search =session.run("""
                    WITH $embedding AS e
                    CALL db.index.vector.queryNodes('recEmb',5, e) yield node as m, score
                    CALL {
                    WITH m
                    MATCH (m)-[r:!RATED]->(target)
                    RETURN coalesce(m.receta_nombre) + " " + type(r) + " " + coalesce(target.name, target.title) AS result
                    UNION
                    WITH m
                    MATCH (m)<-[r:!RATED]-(target)
                    RETURN coalesce(target.name, target.receta_nombre) + " " + type(r) + " " + coalesce(m.receta_nombre) AS result
                    }
                    RETURN result LIMIT 100
                    """,{'embedding': text_embeddings})
                               
    df =  vector_search.to_df()
    
    return df

with GraphDatabase.driver(URI, auth=AUTH) as driver:
   driver.verify_connectivity()
   print("############ Connected to Neo4j #############")
   
    #meter el embbeding en el nodo

   session = driver.session()
   #add_emb2Node(session, text_embeddings)
   #get_all_nodes(session)

   #Vector search:
   result = get_similar_vector(session, text_embeddings)
   print(result)

   #get_similar_nodes(session, text_embeddings)
   #emb_df =  result.to_df()
   #emb=emb_df.iloc[0]['r.embedding']
   #print(emb)



   print("clossing connection...")
    