"""
1- scrtip para conectarse a la base de datos de Neo4j.
2- Se utiliza Langchain para hacer embedding de los textos y hacer pruebas de similitud.
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


#TODO pasar la dimension del vector
embeddings_model  = OpenAIEmbeddings(openai_api_key=apikey) #dimension por defecto 1536
                 


URI = "bolt://localhost:7687"
AUTH = ("neo4j", "adminadmin")

with GraphDatabase.driver(URI, auth=AUTH) as driver:
   driver.verify_connectivity()
   print("############ Connected to Neo4j #############")
    
   session = driver.session()

   result = session.run("""

                MATCH (r:Receta)
            
                RETURN r.receta ,r.embedding


                  """)
   recetas_df = result.to_df()

   
   receta = recetas_df.iloc[0]['r.receta']

   embedded_query = embeddings_model.embed_query(receta)
#
   # Insertar un embedding al nodo
   #query = session.run("""
   #      MATCH (r:Receta)
   #      SET r.embedding = $embedded_query
   #      RETURN r.receta, r.embedding
   #      """, {'embedded_query': embedded_query})
#
   #query_df = query.to_df()


   query_vector = embeddings_model.embed_query('bacalao')


   print(query_vector)
   # Buscar nodos similares a recetas
   res_df = session.run("""
   CALL db.index.vector.queryNodes('ans-emb', 1536, $queryVector)
   YIELD node AS similarDocuments, score
   MATCH (similarDocuments)<-[:HAS]-(r:Receta)
   RETURN r.receta as recta, avg(score) AS score
   ORDER BY score DESC LIMIT 100
   """, {'queryVector': query_vector})
   
   print(res_df.to_df())

   
#crear un indice para el vector
"""
Crear vector index
CREATE vector INDEX `ans-emb` for (r:Receta) on (r.embedding) OPTIONS {indexConfig:{ `vector.dimensions`: 1536,
`vector.similarity_function`: 'cosine'}}
"""