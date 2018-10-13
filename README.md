# Shopping Webapp

## Introduction

This is a shopping portal in which sellers can sell products and customer can search and buy products.

This webapp has been made using flask in python.

## Structure

The application demonstrates Object Oriented Programming and MVC architecture in Python.

## Features

- User can login/signup to buy/sell things
- Passwords are stored in database after hashing
- Homepage contains two sections - All Products and Latest Products
- Products are categorized into 5 categories and several different subcategories
- There is a search bar which can be used to filter products
- After searching, products can be filtered on the basis of price
- Products can be added to cart
- In My Cart, All selected products are listed which can be deleted or can be checked out
- Actual payment is not implemented
- In seller portal, seller can add products to sell after filling a few details

## Running the program

- First, install all the requirements:
    - `sudo apt-get update`
    - `sudo apt-get install python3.6`
    - `pip3 install Flask`
    - `pip3 install Flask-SQLAlchemy`
    - `pip3 install flask-hashing`
    - `pip3 install flask-uploads`
- Open the directory containing all code
- Use command
    - `python3 app.py`
- Open the this [url](http://127.0.0.1:5000) on browser

## File Structure

 * [app.py](./app.py)
 * [model.py](./model.py)