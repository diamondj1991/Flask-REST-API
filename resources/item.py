from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from models.item import ItemModel


class Item(Resource):
    parser = reqparse.RequestParser()
    # this means that basically we can only pass 'price' in the json payload. 'name' can only come from the URL
    # when we do item.update(data)
    parser.add_argument('price', type=float, required=True, help="This field cannot be left blank!")
    parser.add_argument('store_id', type=float, required=True, help="Every item needs a store ID!")

    @jwt_required()
    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json()
        return {'message': 'Item not found'}, 404

    def post(self, name):
        if ItemModel.find_by_name(name):
            return {"message": "An item with the name '{}' already exists.".format(name)}, 400

        data = Item.parser.parse_args()

        item = ItemModel(name, data['price'], data['store_id'])

        try:
            item.save_to_db()
        except:
            return {'message': 'An error occurred inserting the item'}, 500

        return item.json(), 201

    def delete(self, name):
        item = ItemModel.find_by_name(name)

        if not item:
            return {"message": "An item with the name '{}' doesn't exist.".format(name)}, 404
        else:
            item.delete_from_db()

        return {'message': 'Item Deleted'}

    def put(self, name):
        data = Item.parser.parse_args()

        item = ItemModel.find_by_name(name)

        if item is None:
            item = ItemModel(name, data['price'], data['store_id'])
        else:
            item.price = data['price']
            item.store_id = data['store_id']

        item.save_to_db()

        return item.json()


class ItemList(Resource):
    def get(self):
        return {'items': [item.json() for item in ItemModel.query.all()]}
