from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import ItemModel
from schemas import ItemSchema, ItemUpdateSchema

blp = Blueprint("Items", __name__, description="Operations on items")


@blp.route("/item/<int:item_id>")
class Item(MethodView):
    @blp.response(200, ItemSchema)
    def get(self, item_id):
        if not(isinstance(item_id,int)):
            abort(400, message="Item ID must be an integer and cannot be empty")
        item = ItemModel.query.get_or_404(item_id)
        return item

    @jwt_required()
    def delete(self, item_id):   
        if not(isinstance(item_id,int)):
            abort(400, message="Item ID must be an integer and cannot be empty")         
        item = ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return{"message":"Item deleted."}

    @blp.arguments(ItemUpdateSchema)
    @blp.response(200, ItemSchema)
    def put(self, item_data, item_id):
        if not(isinstance(item_id,int)):
            abort(400, message="Item ID must be an integer and cannot be empty")
        item = ItemModel.query.get(item_id)
        if item:
            if not (isinstance(item_data['price'],float)):
                abort(400,message="Price must be a float and cannot be empty")
            if not(isinstance(item_data['quantity'],int)):
                abort(400,message="Quantity must be an integer and cannot be empty") 
        else:
            item = ItemModel(id=item_id, **item_data)

        db.session.add(item)
        db.session.commit()
        
        return item


@blp.route("/item")
class ItemList(MethodView):
    @jwt_required()
    @blp.response(200, ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all()

    @jwt_required(fresh=True)
    @blp.arguments(ItemSchema)
    @blp.response(200, ItemSchema)
    def post(self, item_data):
        item = ItemModel(**item_data)
        if not(isinstance(item_data['store_id'],int)):
            abort(400, message="Store ID must be an integer and cannot be empty")
        if not (isinstance(item_data['price'],float)):
            abort(400,message="Price must be a float and cannot be empty")
        if not(isinstance(item_data['quantity'],int)):
            abort(400,message="Quantity must be an integer and cannot be empty")
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the item.")

        return item