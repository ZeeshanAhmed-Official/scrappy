from flask import Flask, request
from flask import jsonify, make_response
from database import Database

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

# Check for Authorization via API KEY
@app.before_request
def hook():
    if 'apikey' in request.headers:
        apikey = request.headers.get('apikey')
        db = Database()
        if not db.checkIfAuthenticated(apikey):
            return make_response(jsonify(
                success="NO",
                status_code="401 Unauthorized",
            ), 401)
    else:
        return make_response(jsonify(
            success="NO",
            status_code="401 Unauthorized",
        ), 401)


# Provide product information given SKU
@app.route('/api/productref/<sku>')
def product_info(sku):
    if sku:
        db = Database()
        data = db.getProductDetails(sku)
        if data:
            db.closeConnection()
            return make_response(jsonify(
                success="YES",
                status_code="201 OK",
                body=data
            ), 200)

    return make_response(jsonify(
        success="NO",
        status_code="202 OK",
        body='No Product(s) here'
    ), 202)


# Update Y Flag for a product
@app.route('/api/yflagupdate/<sku>', methods = ['POST'])
def yflag_update(sku):
    category_id = request.args.get('category_id')
    if sku:
        db = Database()
        updated = db.updateProductFlagStatus(sku, 'N', 'Y')

        if updated:
            db.closeConnection()
            return make_response(jsonify(
                success="YES",
                status_code="201 OK",
                body={
                    'sku': sku,
                    'FLAG_STATUS': 'Y'
                }
            ), 200)

    return make_response(jsonify(
        success="NO",
        status_code="202 OK",
        body='No Product(s) here'
    ), 202)


# Update N Flag for a product
@app.route('/api/nflagupdate/<sku>', methods = ['POST'])
def ynlag_update(sku):
    category_id = request.args.get('category_id')
    if sku:
        db = Database()
        updated = db.updateProductFlagStatus(sku, 'Y', 'N')
        if updated:
            db.closeConnection()
            return make_response(jsonify(
                success="YES",
                status_code="201 OK",
                body={
                    'sku': sku,
                    'FLAG_STATUS': 'N'
                }
            ), 200)

    return make_response(jsonify(
        success="NO",
        status_code="202 OK",
        body='No Product(s) here'
    ), 202)


# Provide all products with N Flag
@app.route('/api/nflags')
def nflag_list():
    db = Database()
    data = db.getFlagStatusProducts('N')
    if data:
        db.closeConnection()
        return make_response(jsonify(
            success="YES",
            status_code="201 OK",
            body=data
        ), 200)

    return make_response(jsonify(
        success="NO",
        status_code="202 OK",
        body='No Product(s) here'
    ), 202)


# Provide all products with Y Flag
@app.route('/api/yflags')
def yflag_list():
    db = Database()
    data = db.getFlagStatusProducts('Y')
    if data:
        db.closeConnection()
        return make_response(jsonify(
            success="YES",
            status_code="201 OK",
            body=data
        ), 200)

    return make_response(jsonify(
        success="NO",
        status_code="202 OK",
        body='No Product(s) here'
    ), 202)


# Provide a list of Product Categories
@app.route('/api/categorylist')
def category_listing():
    db = Database()
    data = db.getCategoryList()
    if data:
        db.closeConnection()
        return make_response(jsonify(
            success="YES",
            status_code="201 OK",
            body=data
        ), 200)

    return make_response(jsonify(
        success="NO",
        status_code="202 OK",
        body='No Category(ies) here'
    ), 202)


# Provide all products having the “+” (plus) symbol in the SKU field
@app.route('/api/plusfactor/')
def plusfactor_products():
    db = Database()
    data = db.getProductDetails("+")
    if data:
        db.closeConnection()
        return make_response(jsonify(
            success="YES",
            status_code="201 OK",
            body=data
        ), 200)

    return make_response(jsonify(
        success="NO",
        status_code="202 OK",
        body='No product(s) here'
    ), 202)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
