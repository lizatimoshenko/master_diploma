from py2neo import Graph
import pyorient
from pyorient import OrientDB
from pyorient.ogm import Graph
from arango import ArangoClient
from arango_orm import Database


class Neo4JDataBase:

    @staticmethod
    def connect():
        return Graph("http://localhost:7474/db/data/", auth=("neo4j", "liza"))


class OrientDataBase:

    @staticmethod
    def connect():
        client = OrientDB("localhost", 2424)
        client = client.db_open("books", "root", "root", pyorient.DB_TYPE_GRAPH)

        graph = Graph(pyorient.ogm.Config.from_url("localhost" + ":" + str("2424") +
                                                  "/" + "books", "root", "root"))
        return client, graph


class ArangoDataBase:

    @staticmethod
    def connect():
        client = ArangoClient(protocol='http', host='localhost', port=8529)
        test_db = client.db('books', username='root', password='root')
        return Database(test_db)
