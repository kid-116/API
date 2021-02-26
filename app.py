from flask import Flask, jsonify
from flask_restful import Api, Resource, reqparse
from flask import make_response
import random

## Add Authentication 
from flask_httpauth import HTTPBasicAuth

## Auth Code Start
auth = HTTPBasicAuth()

# Add Users
users = {
    "kid-116": "123",
    "public": "public"
}

# Get Password mechanism 
@auth.get_password
def get_pass(username):
    if username in users:
        return users.get(username)
    return None

## Auth Code End

app = Flask(__name__)
api = Api(app)

dev_reviews = []

class search(Resource):
  def get(self):
    parser = reqparse.RequestParser()
    parser.add_argument("city")
    parser.add_argument("category")
    parser.add_argument("name")
    params = parser.parse_args()
    search_results = []
    if params["city"]:
      search_results = [review for review in dev_reviews if review["city"] == params["city"]]
    if params["category"]:
      search_results = [review for review in search_results if review["category"] == params["category"]]
    if params["name"]:
      search_results = [review for review in search_results if review["name"] == params["name"]]
    if not search_results:
      return "No matching results", 404
    else:
      return search_results, 200

class review(Resource):
    def get(self, id=-1):
        if id == -1:
            return random.choice(dev_reviews), 200
        for review in dev_reviews:
            if(review["id"] == id):
                return review, 200
        return "Review not found", 404
      
class adreview(Resource):
    @auth.login_required
    def post(self):
      parser = reqparse.RequestParser()
      parser.add_argument("id",type=int,required=True)
      parser.add_argument("author",required=True)
      parser.add_argument("rating",required=True)
      parser.add_argument("city", required=True)
      parser.add_argument("category", required=True)  
      parser.add_argument("name", required=True)
      parser.add_argument("comments")
      params = parser.parse_args()
      rating = int(params["rating"])
      ## Validations
      if rating < 0 or rating > 5:
          return make_response(jsonify({'error': 'Invalid entry for rating. Should be between 0 and 5 (inclusive)'}), 400)
      id = params["id"]
      if int(id) < 0:
          return make_response(jsonify({'error': 'Invalid entry for id'}), 400)
      for review in dev_reviews:
          if(id == review["id"]): 
              return make_response(jsonify({'error': 'Review with this id already exists add new id'}), 400)
      review = {
          "id": int(id),
          "author": params["author"],
          "comments": params["comments"],
          "rating": rating,
          "city": params["city"],
          "category": params["category"],
          "name": params["name"],
      }
      dev_reviews.append(review)
      return review, 201

    def put(self):
      parser = reqparse.RequestParser()
      parser.add_argument("id",type=int,required=True)
      parser.add_argument("author")
      parser.add_argument("rating")
      parser.add_argument("city")
      parser.add_argument("category")  
      parser.add_argument("name")
      parser.add_argument("comments")
      params = parser.parse_args()
      id = int(params["id"])
      for obj in dev_reviews:
          if(id == obj["id"]):
              if params["author"]:
                obj["author"] = params["author"]
              if params["rating"]:
                rating = int(params["rating"])
                if rating < 0 or rating > 5:
                  return make_response(jsonify({'error': 'Invalid entry for rating. Should be between 0 and 5 (inclusive)'}), 400)
                obj["rating"] = rating
              if params["city"]:
                obj["city"] = params["city"]
              if params["category"]:
                obj["category"] = params["category"]
              if params["name"]:
                obj["name"] = params["name"]
              if params["comments"]:
                obj["comments"] = params["comments"]      
              return obj, 204
      else:
            return make_response(jsonify({'error': 'id is not present in database'}), 404)

    def delete(self, id='c'):
        if id is 'c':
          return make_response(jsonify({'error': 'id is missing'}), 400)
        global dev_reviews
        dev_reviews = [review for review in dev_reviews if review["id"] != id]
        return f"Review with id {id} is deleted.", 200


class home(Resource):
  def get(self):
    return "Hey there! This is a simple api to write and view reviews on places around your city"

api.add_resource(search, "/search", "/search/")
api.add_resource(review, "/review", "/review/", "/review/<int:id>")
api.add_resource(home,"/")
api.add_resource(adreview,"/adreview/<int:id>","/adreview/","/adreview")

# For Error Handling Best Practises

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized Access'}), 401)