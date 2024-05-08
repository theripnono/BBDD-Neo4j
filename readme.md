# Base de Datos para Neo4j

Creacion de base de datos de grafos de recetas e ingredientes.
Saber los ingredientes que lleva cada receta

2 Nodos -> ingredientes & recetas:

    1 receta --> N ingredientes

3 tablas:


    ingredientes cols:
        id_ingredientes
        ingredientes


    recetas cols:
        id_recetas
        recetas

    [Tabla relacion de los dos nodos]
    rel_ing_y_rec:
    
        id_receta
        id_ingredientes

## Table of Contents

- [Installation](#installation)

## Installation

Es necesario instalar Python y Neo4j.




