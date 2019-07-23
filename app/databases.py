import py2neo
import pyorient
import arango
import arango_orm


class Neo4JDataBase:

    @staticmethod
    def connect():
        graph = py2neo.Graph("http://localhost:7474/db/data/", auth=("neo4j", "liza"))

        return graph


class OrientDataBase:

    @staticmethod
    def connect():
        client = pyorient.OrientDB("localhost", 2424)
        client = client.db_open("books", "root", "root", pyorient.DB_TYPE_GRAPH)

        graph = pyorient.ogm.Graph(pyorient.ogm.Config.from_url("localhost" + ":" + str("2424") +
                                                  "/" + "books", "root", "root"))
        return client, graph


class ArangoDataBase:

    @staticmethod
    def connect():
        client = arango.ArangoClient(protocol='http', host='localhost', port=8529)
        test_db = client.db('books', username='root', password='root')
        return arango_orm.Database(test_db)

    @staticmethod
    def create():
        client = arango.ArangoClient(protocol='http', host='localhost', port=8529)
        sys_db = client.db('_system', username='root', password='root')
        sys_db.create_database('books')

