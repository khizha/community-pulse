from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from app.models import db, Category
from app.schemas.questions import CategoryCreate, CategoryRead, CategoryUpdate

categories_bp = Blueprint(
    "categories",
    __name__,
    url_prefix="/categories",
)

@categories_bp.route("", methods=["POST"])
def create_category():
    payload = request.get_json(silent=True)

    if payload is None:
        return jsonify({
            "error": "Invalid or missing JSON body"
        }), 400

    try:
        category_in = CategoryCreate.model_validate(payload)
    except ValidationError as exc:
        return jsonify({
            "error": "Validation error",
            "messages": exc.errors(),
        }), 422

    category = Category(
        name=category_in.name
    )

    db.session.add(category)
    db.session.commit()

    return jsonify(
        CategoryRead.model_validate(category).model_dump()
    ), 201


@categories_bp.route("", methods=["GET"])
def get_categories():
    categories = db.session.scalars(
        db.select(Category)
    ).all()

    result = [
        CategoryRead.model_validate(category).model_dump()
        for category in categories
    ]

    return jsonify(result), 200


def _get_category_or_404(category_id: int):
    category = db.session.get(Category, category_id)

    if category is None:
        return None, (
            jsonify({
                "error": f"Category with id={category_id} not found"
            }),
            404,
        )

    return category, None


@categories_bp.route("/<int:category_id>", methods=["PUT"])
def update_category(category_id: int):
    category, error = _get_category_or_404(category_id)

    if error:
        return error

    payload = request.get_json(silent=True)

    if payload is None:
        return jsonify({
            "error": "Invalid or missing JSON body"
        }), 400

    try:
        category_in = CategoryUpdate.model_validate(payload)
    except ValidationError as exc:
        return jsonify({
            "error": "Validation error",
            "messages": exc.errors(),
        }), 422

    if category_in.name is not None:
        category.name = category_in.name

    db.session.commit()

    return jsonify(
        CategoryRead.model_validate(category).model_dump()
    ), 200

@categories_bp.route("/<int:category_id>", methods=["DELETE"])
def delete_category(category_id: int):
    category, error = _get_category_or_404(category_id)

    if error:
        return error

    db.session.delete(category)
    db.session.commit()

    return "", 204