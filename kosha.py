from flask import Flask, json, jsonify, make_response, request, session
import recommender
from uuid import uuid4

app = Flask(__name__)
app.debug = True
app.secret_key = 'development key'

data = recommender.load("restaurant_data.csv")

class BusinessData:
  def __init__(self):
    with open('restaurant_data.json') as f:
      self.restaurants = [json.loads(line) for line in f.readlines()]
  def filter(self, name, max_count=30):
    restaurants = self.restaurants
    if name:
      lower_name = name.lower()
      restaurants = [r for r in restaurants if lower_name in r['name'].lower()]
    if max_count and len(restaurants) > max_count:
      restaurants = restaurants[0 : max_count]
    return restaurants
business_data = BusinessData()

@app.route("/")
def main():
  return app.send_static_file("index.html")

@app.route("/restaurants", methods=["GET"])
def api_restaurants():
  restaurant_name = request.args.get('name')
  if restaurant_name:
    recommendations = business_data.filter(restaurant_name)
  elif not "id" in session:
    # New user
    session["id"] = str(uuid4())
    recommendations = recommender.recommend_by_popularity(data)
  else:
    # Existing user.
    recommendations = recommender.recommend_for_user(data, session["id"])

  response = jsonify(items=recommendations)
  response.status_code = 200
  return response

@app.route("/restaurants/<id>", methods=["PATCH"])
def api_post_rating(id):
  global data
  rating = request.json["rating"]
  print id
  print rating
  data = recommender.add_rating(data, id, session["id"], rating)
  print len(data)
  response = make_response()
  response.status_code = 204
  return response

if __name__ == "__main__":
  app.run()
