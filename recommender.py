import graphlab as gl
import pandas as pd

MAX_COUNT = 30

def train_restaurant_data():
    #import matplotlib.pyplot as plt

    filepath = "restaurant_data.csv"
    data = gl.SFrame.read_csv(filepath, column_type_hints={"rating":int})
    #data.show()

    #high_rated_data = data[data["rating"] >= 3]
    #low_rated_data = data[data["rating"] < 3]
    #train_set_1, test_set = gl.recommender.util.random_split_by_user(
                                    #high_rated_data, user_id='user', item_id='restaurant')
    #train_set = train_set_1.append(low_rated_data)
    (train_set, test_set) = gl.recommender.util.random_split_by_user(data, user_id='user', item_id='restaurant',
        max_num_users=1000, item_test_proportion=0.2)
    #(train_set, test_set) = data.random_split(0.8)
    m1 = gl.popularity_recommender.create(train_set, 'user', 'restaurant_id', 'rating')
    baseline_rmse = gl.evaluation.rmse(test_set['rating'], m1.predict(test_set))
    print baseline_rmse

    regularization_vals = [0.001, 0.01, 0.05, 0.1]
    number_of_factors = [2, 5, 10, 25]
    models = [gl.factorization_recommender.create(train_set, 'user', 'restaurant_id', 'rating',
                                              max_iterations=50, num_factors= 25, regularization= 0.01, verbose = False)]

    # Save the train and test RMSE, for each model
    (rmse_train, rmse_test) = ([], [])
    for m in models:
        rmse_train.append(m['training_rmse'])
        rmse_test.append(gl.evaluation.rmse(test_set['rating'], m.predict(test_set)))

    print rmse_train
    print rmse_test

def load(filepath):
    return gl.SFrame.read_csv(filepath, column_type_hints={"rating":int})

def add_rating(data, id, user, rating):
    name = data[data["id"] == id]["name"][0]
    new_rating = gl.SFrame({"id": [id], "name" : [name], "user": [user], "rating":[rating], "X1":["X1"]})
    return data.append(new_rating)

def get_rating(data, id, user):
    return 3

def recommend_for_user(data, user, max_count=MAX_COUNT):
    mf_model = gl.ranking_factorization_recommender.create(
        data, 'user', 'id', 'rating',
        max_iterations=10, num_factors=25, regularization=0.01, verbose=True)
    model_recommendations = mf_model.recommend(users=[user], k=max_count)
    recommendations_data = model_recommendations.to_dataframe()
    recommendations = []
    for index, rows in recommendations_data.iterrows():
        id = rows["id"]
        name = data[data["id"] == id]["name"][0]
        recommendations.append({"id":id, "name":name, "rating" : rows["score"]})
    return recommendations

def recommend_by_popularity(data, max_count=MAX_COUNT):
    m = gl.popularity_recommender.create(data, 'user', 'id', 'rating', verbose=False)
    model_recommendations = m.recommend(k=5)

    recommendations_data = model_recommendations.to_dataframe()
    recommendations = []
    for index, rows in recommendations_data.iterrows():
        if index >= max_count: break
        id = rows["id"]
        name = data[data["id"] == id]["name"][0]
        recommendations.append({"id":id, "name":name, "rating" : rows["score"]})
    return recommendations

def main():
    data = load("restaurant_data.csv")
    recommendations = recommend_by_popularity(data)
    print recommendations

if __name__ == '__main__':
    main()
