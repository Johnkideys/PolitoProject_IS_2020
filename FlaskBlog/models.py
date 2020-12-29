from datetime import datetime
from FlaskBlog import db, login_manager
from flask_login import UserMixin, current_user


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))




class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='defaultprofilepic.jpg')
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(15), nullable=False)
    check = db.Column(db.Integer, nullable=False, default=0)
    posts = db.relationship('Post', backref='author', lazy=True)
    products = db.relationship('ProductItem', backref='producer', lazy=True)
    userorders = db.relationship('PurchaseInfo', backref='buyer', lazy=True)
    usercomments = db.relationship('Comments', backref='personwhocommented', lazy=True)

    def __repr__(self):
        return "User(%r, %r, %r)" % (self.username, self.email, self.image_file)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    image_farm_file = db.Column(db.String(20), nullable=False, default='farm_pic.jpg')
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_order_farms = db.relationship('PurchaseInfo', backref='farm_that_sold', lazy=True)
    user_order_comment_farms = db.relationship('Comments', backref='farm_got_commented', lazy=True)
    city = db.Column(db.String(20), nullable=False, default='Torino')

    def __repr__(self):
        return "Post(%r, %r)" % (self.title, self.date_posted)


class ProductItem(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=False)
    descr = db.Column(db.Text, unique=True, nullable=True)
    price = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    cartitems = db.relationship('PurchaseInfo', backref='product_name', lazy=True)

    #cartitems = db.relationship('CartItem', backref='Product')

    def __repr__(self):
        return '<ProductName %r>' % self.name

class PurchaseInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    delivery = db.Column(db.String(100), nullable=False, default='pick up')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    good_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)

class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title_comment = db.Column(db.String(100), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
