from flask import Flask, jsonify
import recommender

app = Flask(__name__)
app.debug = True

@app.route("/")
def main():
  return app.send_static_file("index.html")

@app.route("/restaurants", methods=["GET"])
def api_restaurants():
  recommendations = recommender.get_recommendations()
  response = jsonify(items=recommendations)
  response.status_code = 200
  return response

if __name__ == "__main__":
  app.run()
