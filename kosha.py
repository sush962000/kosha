from flask import Flask, jsonify, make_response, request
import recommender
import json

app = Flask(__name__)
app.debug = True

data = recommender.load("restaurant_data.csv")

@app.route("/")
def main():
  return app.send_static_file("index.html")

@app.route("/restaurants", methods=["GET"])
def api_restaurants():
  recommendations = recommender.get_recommendations(data)
  response = jsonify(items=recommendations)
  response.status_code = 200
  return response

@app.route("/restaurants/<id>", methods=["PATCH"])
def api_post_rating(id):
  print id
  print request.json
  #recommender.add_new_data(id, rating)
  response = make_response()
  response.status_code = 204
  return response

if __name__ == "__main__":
  app.run(host="0.0.0.0")
