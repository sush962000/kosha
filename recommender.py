import graphlab as gl

def _has_user(observation_data, user_id):
  # Returns True if the observation_data has the given user_id.
  if not observation_data:
    return False
  return user_id in observation_data['user_id']

class Recommender:
  def __init__(self, observation_data_filepath, item_data_filepath):
    self.observation_data = gl.SFrame.read_csv(
        observation_data_filepath,
        column_type_hints={"rating":int})
    self.item_data = gl.SFrame.read_csv(item_data_filepath)
    self.new_observation_data = None
    self.popularity_recommender = gl.popularity_recommender.create(
        self.observation_data,
        target='rating',
        verbose=False)
    self.ranking_factorization_recommender = gl.ranking_factorization_recommender.create(
        self.observation_data,
        target='rating',
        num_factors=25,
        regularization=0.01,
        max_iterations=10,
        verbose=False)

  def add_rating(self, user_id, item_id, rating):
    row = gl.SFrame({
        'user_id': [user_id],
        'item_id': [item_id],
        'rating': [rating]
    })
    self.new_observation_data = \
        self.new_observation_data.append(row) if self.new_observation_data else row

  def recommend(self, user_id, max_count=30, name_filter=None):
    recommender = self.ranking_factorization_recommender \
        if self.__is_existing_user(user_id) else self.popularity_recommender
    top_items = recommender.recommend(
        users=[user_id],
        k=max_count,
        items=self.__filter_items(name_filter) if name_filter else None,
        new_observation_data=self.new_observation_data,
        verbose=False)
    return self.__to_json(top_items)

  def __is_existing_user(self, user_id):
    # Returns True if the given user has rated at least one restaurant.
    return _has_user(self.new_observation_data, user_id) #or has_user(self.observation_data)

  def __filter_items(self, name_filter):
    # Returns an item_id SArray that satisfies the given filter.
    item_ids = []
    lower_name = name_filter.lower().encode('utf-8')
    for index, name in enumerate(self.item_data['name']):
      if lower_name in name.lower():
        item_ids.append(self.item_data['item_id'][index])
    return item_ids

  def __to_json(self, top_items):
    recommendations = []
    for index, item_id in enumerate(top_items['item_id']):
      name = self.item_data[self.item_data['item_id'] == item_id]['name'][0]
      cuisine = self.item_data[self.item_data['item_id'] == item_id]['cuisine'][0]
      rating = top_items['score'][index]
      recommendations.append({'id':item_id, 'name':name, 'cuisine':cuisine, 'rating':rating})
    return recommendations

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
    (train_set, test_set) = gl.recommender.util.random_split_by_user(
        data, user_id='user', item_id='restaurant', max_num_users=1000, item_test_proportion=0.2)
    #(train_set, test_set) = data.random_split(0.8)
    m1 = gl.popularity_recommender.create(train_set, 'user', 'restaurant_id', 'rating')
    baseline_rmse = gl.evaluation.rmse(test_set['rating'], m1.predict(test_set))
    print baseline_rmse

    regularization_vals = [0.001, 0.01, 0.05, 0.1]
    number_of_factors = [2, 5, 10, 25]
    models = [gl.factorization_recommender.create(
        train_set, 'user', 'restaurant_id', 'rating', max_iterations=50, num_factors= 25,
        regularization= 0.01, verbose = False)]

    # Save the train and test RMSE, for each model
    (rmse_train, rmse_test) = ([], [])
    for m in models:
        rmse_train.append(m['training_rmse'])
        rmse_test.append(gl.evaluation.rmse(test_set['rating'], m.predict(test_set)))

    print rmse_train
    print rmse_test

def main():
    engine = Recommender("observation_data.csv", "item_data.csv")
    recommendations = engine.recommend('foo')
    print recommendations

if __name__ == '__main__':
    main()
