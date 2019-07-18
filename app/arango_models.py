from arango import DocumentInsertError
from arango_orm.exceptions import DocumentNotFoundError
from arango_orm.fields import String, Integer
from arango_orm import Collection, Relation, Graph, GraphConnection
from passlib.hash import sha256_crypt
from .databases import ArangoDataBase


#sys_db = client.db('_system', username='root', password='root')
#sys_db.create_database('books')


db = ArangoDataBase.connect()


class User(Collection):

    __collection__ = 'users'

    _key = Integer(required=True)  # user_id
    username = String(required=True)
    password = String(required=True, allow_none=False)

    def find(self, username):
        try:
            user = db.query(User).filter_by(username)  # is it correct?
            return user
        except DocumentNotFoundError:
            return None

    def register(self, user_id, password, username):
        if not self.find(username):
            try:
                user = User(_key=user_id, username=username, password=sha256_crypt.encrypt(password))
                db.add(user)
            except DocumentInsertError:
                return None
            return True

        return False

    def verify_password(self, password, username):
        user = self.find(username)
        print(user)
        if not user:
            return False

        return sha256_crypt.verify(password, user.password)

    @staticmethod
    def get_all_users():
        users = db.query(User).all()

        return [u.username for u in users]


class Book(Collection):
    __collection__ = "books"

    _key = Integer(required=True)  # book_id
    authors = String(required=True)
    publication = Integer(required=True)
    title = String(required=True)
    language = String(required=True)

    @staticmethod
    def add_book(book_id, authors, publication, title, language):
        book = Book(
                    _key=book_id,
                    authors=authors,
                    publication=publication,
                    title=title,
                    language=language)
        db.add(book)

        return True

    @staticmethod
    def get_all_books():
        books = db.query(Book).all()
        print(type(books))
        return True

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
    __collection__ = "tags"

    _key = Integer(required=True)  # tag_id
    tag_name = String(required=True)

    @staticmethod
    def add_tag(tag_id, tag_name):
        tag = Tag(
            _key=tag_id,
            tag_name=tag_name
        )

        db.add(tag)

        return True

    @staticmethod
    def get_tag(book_id):
        book = db.query(Book).by_key(book_id)
        graph.expand(book, depth=1, direction='any')
        tags = [tag._object_from.tag_name for tag in book._relations["tagged_to"]]
        return tags


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


def add_tag_to_book(book_id, tag_id):
    book = db.query(Book).by_key(book_id)
    tag = db.query(Tag).by_key(tag_id)
    db.add(graph.relation(book,  Relation("tagged_to"), tag))

    return True


def add_read_books(user_id, book_id):
    book = db.query(Book).by_key(book_id)
    user = db.query(User).by_key(user_id)
    db.add(graph.relation(user,  Relation("reads"), book))

    return True


def add_friends_list(user_id, friend_id):
    friend = db.query(User).by_key(friend_id)
    user = db.query(User).by_key(user_id)
    db.add(graph.relation(user,  Relation("follows"), friend))

    return True


def add_liked_books(user_id, book_id):
    book = db.query(Book).by_key(book_id)
    user = db.query(User).by_key(user_id)
    db.add(graph.relation(user,  Relation("likes"), book))

    return True


def clear_graph():
    db.delete_graph('book_graph')
    return True

