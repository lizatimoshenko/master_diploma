from py2neo.ogm import GraphObject, Property, RelatedTo, RelatedFrom
from py2neo import Relationship
from passlib.hash import sha256_crypt
from .databases import Neo4JDataBase

graph = Neo4JDataBase.connect()


class Book(GraphObject):
    """ Class for Book node """

    __primarykey__ = "book_id"

    book_id = Property()
    authors = Property()
    publication = Property()
    title = Property()
    language = Property()

    tags = RelatedFrom("Tag", "TAGGED_TO")
    reader = RelatedFrom("User", "READS")
    likes = RelatedFrom("User", "LIKES")

    @staticmethod
    def add_book(book_id, authors, publication, title, language):
        book = Book()
        book.book_id = book_id,
        book.authors = authors,
        book.publication = publication,
        book.title = title,
        book.language = language

        graph.push(book)

        return True

    @staticmethod
    def books():
        """ Returns list of all books """
        books = graph.run("MATCH (b:Book) RETURN b.username").data()
        return books

    @staticmethod
    def tags(book_id):
        """List of tags for specific book"""
        book = Book.match(graph, book_id).first()
        tags = [tag.tag_name for tag in book.tags]
        return tags

    @staticmethod
    def most_popular_books():
        """ Returns books which are read by most amount of users """
        query = """
                MATCH (book:Book)<-[reads:READS]-(u:User)
                WITH book, count(reads) AS readers
                RETURN book 
                ORDER BY readers  LIMIT 16
                """
        return graph.cypher.execute(query)


class User(GraphObject):
    """ Class for User node """

    __primarykey__ = "username"

    user_id = Property()
    username = Property()
    password = Property()

    books = RelatedTo("Book")
    liked_books = RelatedTo("Book")
    friends = RelatedTo("User")
    followers = RelatedFrom("User", "FOLLOWS")

    def find(self, username):
        """ Find user in database by username """
        user = User.match(graph, username).first()
        return user

    def register(self, user_id, password, username):
        if not self.find(username):
            user = User()
            user.user_id = user_id
            user.username = username
            user.password = sha256_crypt.encrypt(password)
            graph.push(user)
            return True

        return False

    def verify_password(self, password, username):
        user = self.find(username)
        if not user:
            return False

        return sha256_crypt.verify(password, user.password)

    @staticmethod
    def users():
        """Returns list of all users"""
        return graph.run("MATCH (u:User) RETURN u.username").data()

    @staticmethod
    def reads(user_id, book_id):
        """Create relationship (User)-[:READS]->(Book)"""
        book = Book.match(graph, int(book_id)).first()
        user = User.match(graph, int(user_id)).first()
        graph.create(Relationship(user.__node__, "READS", book.__node__))
        return True

    @staticmethod
    def follows(user_id, friend_id):
        """Create relationship (User)-[:FOLLOWS]->(User)"""
        user = User.match(graph, int(user_id)).first()
        friend = User.match(graph, int(friend_id)).first()
        graph.create(Relationship(user.__node__, "FOLLOWS", friend.__node__))
        return True

    @staticmethod
    def likes(user_id, friend_id):
        """Create relationship (User)-[:LIKES]->(Book)"""
        user = User.match(graph, int(user_id)).first()
        friend = User.match(graph, int(friend_id)).first()
        graph.create(Relationship(user.__node__, "LIKES", friend.__node__))
        return True


class Tag(GraphObject):
    """Class for Tag node"""

    __primarykey__ = "tag_id"

    tag_id = Property()
    tag_name = Property()

    tagged_to = RelatedTo("Book")

    @staticmethod
    def add_tag(tag_id, tag_name):
        tag = Tag()
        tag.tag_name = tag_name
        tag.tag_id = tag_id
        graph.push(tag)
        return True

    @staticmethod
    def add_tag_to_book(book_id, tag_id):
        """Create relationship (Tag)-[:TAGGED_TO]->(Book)"""
        book = Book.match(graph, [int(book_id)]).first()
        tag = Tag.match(graph, int(tag_id)).first()
        graph.create(Relationship(tag.__node__, "TAGGED_TO", book.__node__))
        return True


def clear_graph():
    graph.delete_all()
    return True
