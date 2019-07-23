"""Implementation of models for ArangoDB"""
from arango import DocumentInsertError
from arango_orm.exceptions import DocumentNotFoundError
from arango_orm.fields import String, Integer
from arango_orm import Collection, Relation, Graph, GraphConnection
from passlib.hash import sha256_crypt
from .databases import ArangoDataBase

db = ArangoDataBase.connect()


class User(Collection):
    """Class for User node"""
    __collection__ = 'users'

    _key = String(required=True)  # user_id
    username = String(required=True)
    password = String(required=True, allow_none=False)

    def __init__(self, username, password=None, user_id=None):
        self._key = user_id
        self.username = username
        self.password = password

    def find(self):
        """ Return user in database by username """
        try:
            user = db.query(User).filter_by(self.username)  # is it correct?
            return user
        except DocumentNotFoundError:
            return None

    def insert(self, username, password, user_id):
        """ Insert user node to graph """
        if not self.find(username):
            try:
                user = User(_key=user_id, username=username, password=sha256_crypt.encrypt(password))
                db.add(user)
            except DocumentInsertError:
                return None
            return True
        return False

    def verify_password(self, password):
        """ Return if password is valid """
        user = self.find()
        if not user:
            return False
        return sha256_crypt.verify(password, user.password)

    def reads(self, book_id):
        """ Create relationship (User)-[:READS]->(Book) """
        book = db.query(Book).by_key(book_id)
        user = db.query(User).by_key(self.user_id)
        db.add(graph.relation(user, Relation("reads"), book))

    def follows(self, friend_id):
        """ Create relationship (User)-[:FOLLOWS]->(User) """
        friend = db.query(User).by_key(friend_id)
        user = db.query(User).by_key(self.user_id)
        db.add(graph.relation(user, Relation("follows"), friend))

    def likes(self, book_id):
        """ Create relationship (User)-[:LIKES]->(Book) """
        book = db.query(Book).by_key(book_id)
        user = db.query(User).by_key(self.user_id)
        db.add(graph.relation(user, Relation("likes"), book))

    @staticmethod
    def users():
        """Return list of all users"""
        users = db.query(User).all()
        return [u.username for u in users]


class Book(Collection):
    """Class for Book node"""

    __collection__ = "books"

    _key = Integer(required=True)  # book_id
    authors = String(required=True)
    year = Integer(required=True)
    title = String(required=True)
    language = String(required=True)

    def __init__(self, book_id, authors, year, title, language):
        self._key = book_id
        self.authors = authors
        self.year = year
        self.title = title
        self.language = language

    def insert(self):
        """Inserting book node to graph"""
        db.add(self)

    def linked_tags(self):
        """Return list of tags for specific book"""
        book = db.query(Book).by_key(self._key)
        graph.expand(book, depth=1, direction='any')
        tags = [tag._object_from.tag_name for tag in book._relations["tagged_to"]]
        return tags

    @staticmethod
    def books():
        """Return list of all books"""
        books = db.query(Book).all()
        return books


    @staticmethod
    def most_popular_books():
        """ Returns books which are read by most amount of users """
        query = """
                FOR user IN users
                    FOR book IN INBOUND user reads
                        COLLECT book_doc=book WITH COUNT INTO amount
                        SORT book_doc, amount ASC
                        RETURN {"book":book_doc, "count":amount}
                """
        return graph.aql(query)


class Tag(Collection):
    """Class for Tag node"""

    __collection__ = "tags"

    _key = Integer(required=True)  # tag_id
    tag_name = String(required=True)

    def __init__(self, tag_id, tag_name):
        self._key = tag_id
        self.tag_name = tag_name

    def insert(self):
        """ Insert tag to graph"""
        db.add(self)

    def link_to_book(self, tag_id):
        """Create relationship (Tag)-[:TAGGED_TO]->(Book) """
        book = db.query(Book).by_key(self._key)
        tag = db.query(Tag).by_key(tag_id)
        db.add(graph.relation(book, Relation("tagged_to"), tag))
        return True


class TaggedTo(Relation):
    __collection__ = "tagged_to"

    _key = Integer(required=True)


class Reads(Relation):
    __collection__ = "reads"

    _key = Integer(required=True)


class Follows(Relation):
    __collection__ = "follows"

    _key = Integer(required=True)


class Likes(Relation):
    __collection__ = "likes"

    _key = Integer(required=True)


class BooksGraph(Graph):

    __graph__ = 'book_graph'

    graph_connections = [

        GraphConnection(Book, TaggedTo, Tag),
        GraphConnection(User, Reads, Book),
        GraphConnection(User, Follows, User),
        GraphConnection(User, Likes, Book)
    ]


graph = BooksGraph(connection=db)
# db.create_graph(graph)


def clear_graph():
    """Clear data from the graph"""
    db.delete_graph('book_graph')
    return True

