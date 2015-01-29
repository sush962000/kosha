from flask import Flask, jsonify, make_response, request, session
from recommender import Recommender
from uuid import uuid4

app = Flask(__name__)
app.debug = True
app.secret_key = 'development key'

recommender = Recommender(
    observation_data_filepath="observation_data.csv",
    item_data_filepath="item_data.csv")

@app.route("/")
def main():
  return app.send_static_file("index.html")

@app.route("/restaurants", methods=["GET"])
def api_restaurants():
  if not "user_id" in session:
    session["user_id"] = str(uuid4())
  top_items = recommender.recommend(
      user_id=session["user_id"],
      name_filter=request.args.get('name'))
  response = jsonify(items=top_items)
  response.status_code = 200
  return response

@app.route("/restaurants/<item_id>", methods=["PATCH"])
def api_post_rating(item_id):
  rating = request.json["rating"]
  recommender.add_rating(
      user_id=session["user_id"],
      item_id=item_id,
      rating=rating)
  response = make_response()
  response.status_code = 204
  return response

if __name__ == "__main__":
  app.run()
