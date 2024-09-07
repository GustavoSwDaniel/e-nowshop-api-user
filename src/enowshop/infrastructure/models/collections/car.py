from mongoengine import Document, EmbeddedDocument
from mongoengine.fields import StringField, IntField, ListField


class Item(EmbeddedDocument):
    quantity = IntField()
    name = StringField()
    value = IntField()
    image_url = StringField()
    product_uuid = StringField()



class Car(Document):
    meta = {'collection': 'car'}

    user_uuid = StringField(unique=True)
    itens = ListField(EmbeddedDocument(Item))
    created_at = StringField()