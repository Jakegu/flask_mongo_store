from flask import Flask, request, abort
from config import me, db
import json
from bson import ObjectId

app = Flask("server")






@app.get("/")
def home():
    return "Hello World"

@app.get("/about")
def about_me():
    return "Jake Gulotta"

@app.get("/api/about")
def about_data():
    return json.dumps(me)


@app.get("/api/about/developer")
def developer_name():
    full_name = me["name"] + " " + me["last_name"]
    return json.dumps(full_name)

@app.get("/api/categories")
def categories():
    all_cats = []
    cursor = db.products.find({})
    for product in cursor:
        category = product["category"]
        if category not in all_cats:
            all_cats.append(category)

    return json.dumps(all_cats)


def fix_id(record):
    record["_id"] = str(record["_id"])
    return record


@app.get("/api/products")
def get_products():
    products = []
    cursor = db.products.find({})
    for product in cursor:
        products.append(fix_id(product))
    return json.dumps(products)


@app.post("/api/products")
def save_product():
    product = request.get_json()
    db.products.insert_one(product)
    return json.dumps(fix_id(product))



@app.get("/api/products/category/<cat>")
def get_by_category(cat):
    products = []
    cursor = db.products.find({"category": cat })
    for product in cursor:
        products.append(fix_id(product))
    return json.dumps(products)


@app.get("/api/reports/total")
def get_prices_sum():
    
    cursor = db.products.find({})
    sum = 0
    for product in cursor:
        price = product["price"]
        sum += price
    return json.dumps(sum)


@app.get("/api/coupons")
def get_coupons():
    results = []
    cursor = db.coupons.find()
    for coupon in cursor:
        results.append(fix_id(coupon))
    return json.dumps(results)


@app.post("/api/coupons")
def save_coupons():
    coupon = request.get_json()

    if not "code" in coupon:
        return abort(400, "code is required")
    if not "discount" in coupon:
        return abort(400, "discount is required")
    if "discount" > 35:
        return abort(400, "discount must be less than 35%")


    db.coupons.insert_one(coupon)
    return json.dumps(coupon)

@app.get("/api/coupons/code/<code>")
def get_coupon_code(code):
    coupon = db.coupons.find_one({"code": code})
    if not coupon:
        return abort(404, "Coupon not found")
    
    return json.dumps(fix_id(coupon))

@app.get("/api/coupons/id/<id>")
def get_coupon_id(id):
    if not ObjectId.is_valid(id):
        return abort(400, "Invalid id")

    db_id = ObjectId(id)
    coupon = db.coupons.find_one({"_id": db_id})
    if not coupon:
        return abort(404, "Coupon not found")
    
    return json.dumps(fix_id(coupon))

@app.get("/api/products/id/<id>")
def get_prod_id(id):
    if not ObjectId.is_valid(id):
        return abort(400, "Invalid id")
    
    db_id = ObjectId(id)
    product = db.products.find_one({"_id": db_id})
    if not product:
        return abort(404, "Product not found")
    
    return json.dumps(fix_id(product))

app.run(debug=True)