import os
import secrets
from PIL import Image
from flask import render_template, url_for, redirect, flash, request, abort, session
from FlaskBlog import app, db, bcrypt, mail
from FlaskBlog.forms import (RegistrationForm, LoginForm, RetailerForm, UpdateAccountForm,
                             UpdateProductsForm, PurchaseForm, CommentForm, RequestResetForm, ResetPasswordForm)
from FlaskBlog.models import User, Post, ProductItem, PurchaseInfo, Comments
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message, Mail

from functools import wraps
def producer_required(func):
    """
    Modified login_required decorator to restrict access to admin group.
    """

    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_user.role != "producer":
            flash("You don't have permission to access this resource.", "warning")
            return redirect(url_for("home"))
        return func(*args, **kwargs)
    return decorated_view

@app.route('/home')
def home():
    posts = Post.query.filter_by(city='Torino')
    return render_template('home.html', posts=posts)

@app.route('/')
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/registeruser', methods=['GET','POST'])
def registeruser():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, role='user')
        db.session.add(user)
        db.session.commit()
        flash('Account is created, you can now Sign In!','success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/registerproducer', methods=['GET','POST'])
def registerproducer():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, role='producer')
        db.session.add(user)
        db.session.commit()
        flash('Account is created, you can now Sign In!','success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            flash('You have been logged in!', 'success')
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Login failed, Check credentials!', 'danger')
    return render_template('login.html', title='SignIn', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

def save_picture(form_picture):

    fname, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = fname + f_ext
    picture_path = os.path.join(app.root_path, 'static/Pics', picture_fn)
    form_picture.save(picture_path)

    output_size = (325, 325)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route('/account', methods=['GET','POST'])
@login_required
def account():
    form = UpdateAccountForm()
    purchaseinfo = PurchaseInfo.query.filter_by(user_id=current_user.id).all()
    purchaseinfo_producer = PurchaseInfo.query.all()

    products = ProductItem.query.all()
    posts = Post.query.all()
    users = User.query.all()

    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated', 'success')

        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='Pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form,
                           purchaseinfo=purchaseinfo, posts=posts, products=products,
                           users=users, purchaseinfo_producer=purchaseinfo_producer)

@app.route('/create_farm', methods=['GET','POST'])
@login_required
@producer_required
def create_farm():
    if current_user.check == True:
        flash('You already created a farm', 'danger')
        return redirect(url_for('home'))
    picture_file = "farm_pic.jpg"
    form = RetailerForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
        post = Post(title=form.title.data, content=form.content.data, image_farm_file=picture_file, city=form.city.data, author=current_user)

        db.session.add(post)
        current_user.check = 1
        db.session.commit()
        flash('Your farm products page has been created!', 'success')

        image_farm_file = url_for('static', filename='Pics/' + post.image_farm_file)
        return redirect(url_for('home', image=image_farm_file))
    elif request.method == 'GET':
        form.city.data = 'Torino'

    return render_template('create_retailer.html', form=form)

@app.route('/add_products_farm', methods=['GET','POST'])
@login_required
@producer_required
def add_products_farm():
    form = UpdateProductsForm()
    if form.validate_on_submit():
        product = ProductItem(name=form.name.data, descr=form.descr.data, price=form.price.data, producer=current_user)
        db.session.add(product)
        db.session.commit()
        flash('Your farm products have been updated!', 'success')
        post = Post.query.filter_by(user_id=current_user.id).first()
        return redirect(url_for('post', post_id=post.id))
    return render_template('create_retailer_products.html', form=form)


@app.route('/post/<int:post_id>')
@login_required
def post(post_id):

    post = Post.query.get_or_404(post_id)
    products = ProductItem.query.all()
    purchased = PurchaseInfo.query.filter_by(user_id=current_user.id, post_id=post.id)
    comments = Comments.query.filter_by(farm_got_commented=post)

    specific_products=[]
    for product in products:
        if product.user_id == post.user_id:
            specific_products.append(product)

    num = len(specific_products)
    num_range = range(num)
    return render_template('post.html', title=post.title, post=post,
                           specific_products=specific_products, purchased=purchased, comments=comments, num=num, num_range=num_range)

@app.route('/confirmorder/<int:product_id>/<int:post_id>', methods=['GET','POST'])
@login_required
def confirmorder(product_id, post_id):
    product = ProductItem.query.get_or_404(product_id)
    post = Post.query.get_or_404(post_id)
    form = PurchaseForm()
    if form.validate_on_submit():
        purchaseinfo = PurchaseInfo(delivery=form.delivery.data, buyer=current_user, farm_that_sold=post, product_name=product)
        db.session.add(purchaseinfo)
        db.session.commit()
        flash('Succesfully Purchased!', 'success')
        return redirect(url_for('home'))
    elif request.method == 'GET':
        form.delivery.data = 'Pick Up'
    return render_template('confirmorder.html', product=product, form=form)

@app.route('/comments/<int:post_id>', methods=['GET','POST'])
@login_required
def comments(post_id):
    form = CommentForm()
    post = Post.query.get_or_404(post_id)

    if form.validate_on_submit():
        comment = Comments(title_comment=form.title.data, comment=form.comment.data, personwhocommented=current_user,  farm_got_commented=post)
        db.session.add(comment)
        db.session.commit()
        flash('Success!', 'success')
        return redirect(url_for('post', post_id=post_id))
    return render_template('comments.html', form=form)

@app.route('/update_post/<int:post_id>', methods=['POST','GET'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = RetailerForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            post.image_farm_file = picture_file
        post.title = form.title.data
        post.content = form.content.data
        post.city = form.city.data
        db.session.commit()
        flash('Farm details have been changed!', 'success')
        return redirect(url_for('post', post_id=post_id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        form.city.data = post.city
    return render_template('update_farm.html', post=post, form=form)

@app.route('/deletebundle/<int:product_id>', methods=['POST'])
@login_required
def delete_bundle(product_id):
    product = ProductItem.query.filter_by(user_id=current_user.id).all()

    purchase = PurchaseInfo.query.filter_by(good_id=product_id).first()
    if purchase:
        db.session.delete(purchase)
        db.session.commit()
    #if product.user_id != current_user.id:
    #    abort(403)

    for i in range(len(product)):
        if product[i].id == product_id:
            db.session.delete(product[i])
            db.session.commit()
            flash('Your bundle has been deleted!', 'success')

    return redirect(url_for('home'))

def send_mail(to, subject, template, **kwargs):
    msg = Message(subject,
                  recipients=[to],
                  sender='noreply@demo.com')
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = '''To reset your password, visit the following link:
    {y}
    If you did not make this request then simply ignore this email and no changes will be made.
    '''.format(y=url_for('reset_token', token=token, _external=True))
    mail.send(msg)

@app.route('/reset_password', methods=['POST','GET'])
def reset_request():
    #if current_user.is_authenticated():
    #    return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions about how to reset your password', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated():
       return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form )
