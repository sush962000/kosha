from flask import Flask, jsonify, make_response, request
#import recommender
import json

app = Flask(__name__)
app.debug = True

#data = recommender.load("restaurant_data.csv")
with open('restaurant_data.json') as f:
  restaurants = [json.loads(line) for line in f.readlines()]

class Data:
  def __init__(self):
    with open('restaurant_data.json') as f:
      self.restaurants = [json.loads(line) for line in f.readlines()]
      self.restaurants.sort(key=lambda restaurant: restaurant['rating'])
  def filter(self, name, count):
    restaurants = self.restaurants
    if name:
      lower_name = name.lower()
      restaurants = [r for r in restaurants if lower_name in r['name'].lower()]
    if count and len(restaurants) > count:
      restaurants = restaurants[0 : count]
    return restaurants
data = Data()

@app.route("/")
def main():
  return app.send_static_file("index.html")

@app.route("/restaurants", methods=["GET"])
def api_restaurants():
  #recommendations = recommender.get_recommendations(data)
  recommendations = data.filter(name=request.args.get('name'), count=30)
  response = jsonify(items=recommendations)
  response.status_code = 200
  return response

@app.route("/restaurants/<id>", methods=["PATCH"])
def api_post_rating(id):
  rating = request.json["rating"]
  print id
  print rating
  #recommendations = recommender.recommend_for_new_user(data, id, rating)
  response = make_response()
  response.status_code = 204
  return response

if __name__ == "__main__":
  app.run()
