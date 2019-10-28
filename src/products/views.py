from src import app, db

from flask import redirect, render_template, request, url_for, jsonify
from flask_login import login_required

from src.manufacturers.models import Manufacturer
from src.products.models import Product
from src.products.forms import ModelForm


@app.route("/models", methods=["GET"])
def models_index():
    return render_template("models/list.html", models=Product.query.all(), form=ModelForm(),
                           manufExists=Manufacturer.query.count() > 0, listeroo=Product.listByBrokenPercent() )


@app.route("/models/new/")
@login_required
def models_form():
    if Manufacturer.query.count() == 0:
        return redirect(url_for('manufacturers_index'))

    return render_template("models/new.html", form=ModelForm())


@app.route("/models/<model_id>/", methods=["POST"])
@login_required
def model_setEol(model_id):
    m = Product.query.get(model_id)

    if m.eol:
        m.eol = False
    else:
        m.eol = True
    db.session().commit()

    return redirect(url_for("models_index"))


@app.route("/models/<model_id>/addRef/<target_id>", methods=["POST"])
def prodct_addSubcomponent(model_id, target_id):
    m = Product.query.get(model_id)
    t = Product.query.get(target_id)

    m.add_ref(t)
    db.session().commit()
    return ('', 204)

@app.route("/models/<model_id>/removeRef/<target_id>", methods=["POST"])
def prodct_removeSubcomponent(model_id, target_id):
    m = Product.query.get(model_id)
    t = Product.query.get(target_id)

    m.remove_ref(t)
    db.session().commit()
    return ('', 204)

@app.route("/models/<model_id>/", methods=["GET"])
def get_product(model_id):
    p = Product.query.get(model_id)
    return render_template("models/one.html", product = p, manufacturers = Manufacturer.query.all(), counts=p.listByPartCount())

@app.route("/models/", methods=["POST"])
@login_required
def models_create():
    form = ModelForm(request.form)

    if not form.validate():
        return render_template("models/list.html", form=form, models=Product.query.all(), manufExists=Manufacturer.query.count() > 0, listeroo=Product.listByBrokenPercent())

    t = Product(form.name.data)
    t.manufacturer = form.manufacturer.data
    t.eol = False

    db.session().add(t)
    db.session().commit()

    return redirect(url_for("models_index"))

@app.route("/models/<self_id>/checkAllowed-<other_id>", methods=["POST"])
def goNuts(self_id, other_id):
    p = Product.query.get(self_id)
    p2 = Product.query.get(other_id)
    
    if p is p2:
        result = {'success' : 'Not allowed'}
        return jsonify(result), 203
    
    if not p.check_subcomponent_status(p2):
        result = {'success' : 'Not allowed'}
        return jsonify(result), 203
    result = {'success' : 'Allowed'}
    return jsonify(result), 203