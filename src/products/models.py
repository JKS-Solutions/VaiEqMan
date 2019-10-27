import os
from src import db

from sqlalchemy.sql import text

product_subcomponent = db.Table(
    'productsubcomponent',
    db.Column('ProductSubcomponentId', db.Integer, primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id')),
    db.Column('subcomponent_id', db.Integer, db.ForeignKey('product.id'))
)


class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())

    name = db.Column(db.String(144), nullable=False)
    manufacturer_id = db.Column(db.Integer, db.ForeignKey('manufacturer.id'),
                                nullable=False)
    eol = db.Column(db.Boolean, nullable=False)

    subcomponents = db.relationship(
        'Product',
        secondary=product_subcomponent,
        primaryjoin=(id == product_subcomponent.c.subcomponent_id),
        secondaryjoin=(id == product_subcomponent.c.product_id),
        backref=db.backref('products', lazy='dynamic'),
        lazy='dynamic'
    )

    def __init__(self, name):
        self.name = name
        self.eol = False

    def __repr__(self):
        return self.name

    def remove_ref(self, other):
        self.subcomponents.remove(other)

    def add_ref(self, other):
        if self.check_subcomponent_status(other):
            self.subcomponents.append(other)

    def check_subcomponent_status(self, other):
        if self.id is other.id:
            return False  
        return self.isAllowed(other)
                  
    @staticmethod
    def listByBrokenPercent():
        on_heroku = False
        if 'DYNO' in os.environ:
            on_heroku = True

        if not on_heroku:
            # This line works both locally, and using mssql - for some reason psql on heroku does not approve
            stmt = text("SELECT product.id, product.name, "
                        "(SELECT 100.0 * ( SELECT COUNT(*) FROM equipment WHERE equipment.model_id = product.id AND equipment.isbroken) / "
                        "( SELECT COUNT(*) FROM equipment WHERE equipment.model_id = product.id) ) as brokenavg "
                        "FROM product WHERE brokenavg IS NOT NULL GROUP BY product.id ORDER BY brokenavg asc LIMIT 10"
                        )
        else:
            # Add bunch of bubbleghum for heroku psql...
            stmt = text("SELECT product.id, product.name, "
                        "(SELECT 100.0 * ( SELECT COUNT(*) FROM equipment WHERE equipment.model_id = product.id AND equipment.isbroken) "
                        " / NULLIF(( SELECT COUNT(*) FROM equipment WHERE equipment.model_id = product.id), 0) ) "
                        " FROM product WHERE (SELECT 100.0 * ( SELECT COUNT(*) FROM equipment WHERE equipment.model_id = product.id AND equipment.isbroken) "
                        " / NULLIF(( SELECT COUNT(*) FROM equipment WHERE equipment.model_id = product.id), 0) ) "
                        "IS NOT NULL GROUP BY product.id ORDER BY (SELECT 100.0 * ( SELECT COUNT(*) FROM equipment WHERE equipment.model_id = product.id AND equipment.isbroken) "
                        "/ NULLIF(( SELECT COUNT(*) FROM equipment WHERE equipment.model_id = product.id), 0) ) asc LIMIT 10"
                        )

        res = db.engine.execute(stmt)

        response = []
        for row in res:
            response.append(
                {"id": row[0], "name": row[1], "brokenAvg": round(row[2], 3)})
        return response

    
    def isAllowed(self, node):
        children = [node]
        parents = [self]
        visited = []
        
        while parents:
            parent = parents.pop(0)
            visited.append(parent.id)
            for p in parent.products:               
                parents.append(p)
                
        while children:
            child = children.pop(0)
            for c in child.subcomponents:
                if(c.id in visited):
                    return False
                children.append(c)
        
        return True

