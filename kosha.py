from flask import Flask, jsonify, make_response, request
import recommender
import json

app = Flask(__name__)
app.debug = True

restaurants = []
with open("business_data.json") as f:
  restaurants = [json.loads(line) for line in f.readlines()]

@app.route("/")
def main():
  return app.send_static_file("index.html")

@app.route("/restaurants", methods=["GET"])
def api_restaurants():
  #recommendations = recommender.get_recommendations()
  recommendations = restaurants
  response = jsonify(items=recommendations)
  response.status_code = 200
  return response

@app.route("/restaurants/<business_id>", methods=["PATCH"])
def api_post_rating(business_id):
  print business_id
  print request.json
  #recommender.add_new_data(business_id, user_rating)
  response = make_response()
  response.status_code = 204
  return response

if __name__ == "__main__":
  app.run(host="0.0.0.0")
