import sys
import json
import io
import numpy as np
import pandas as pd
import pickle

import matplotlib.pyplot as plt

def create_restaurant_set(business_file, city_to_look_for, categories_to_look_for):
    # first create a list of restaurant_ids in Vegas
    restaurant_set = set()
    business_data = open(business_file)
    for line in business_data:
        business = json.loads(line)
        if business.has_key("categories") and business.has_key("city"):
            business_categories = [category.encode('utf-8').lower() for category in business["categories"]]
            business_city = business["city"].encode('utf-8').lower()
            if any( category in categories_to_look_for for category in business_categories) and business_city == city_to_look_for:
                restaurant_set.add(business["business_id"].encode('utf-8'))
    return(restaurant_set) #4977 restaurants in Las Vegas


def explore_restaurant_data(business_file):
    # check whats all in business data
    business_data = open(business_file)
    n = 0
    for line in business_data:
        if n <= 10:
            business = json.loads(line)
            print business["categories"]
            n += 1



def create_review_dict(review_file, business_file, city_to_look_for, categories_to_look_for):

    reviews = open(review_file)
    restaurant_set = create_restaurant_set(business_file, city_to_look_for, categories_to_look_for)
    review_dict = {}

    for line in reviews:
        review = json.loads(line)
        if review.has_key("business_id") and review["business_id"].encode('utf-8') in restaurant_set:
            if review_dict.has_key(review["business_id"].encode('utf-8')):
                review_dict[review["business_id"].encode('utf-8')][review["user_id"].encode('utf-8')] = review["stars"]
            else:
                review_dict[review["business_id"].encode('utf-8')] = {review["user_id"].encode('utf-8'): review["stars"]}
    return(review_dict) # 4975 restaurants have reviews and a total of 333203 reviews and 105412 users


def get_restaurant_rating_distribution(review_dict):
    restaurant_review_list = []
    for value in review_dict.values():
        restaurant_review_list.append(len(value))
    ser = pd.Series(restaurant_review_list)
    print ser.describe()

    # Original: Min.   :   1.00  1st Qu. :   6.00   Median :  17.00   Mean   :  66.97   3rd Qu.:  57.00  Max.   :3615.00 std : 169.776804
    # Final:    Min.   :   1.00  1st Qu. :   4.00   Median :  10.00   Mean   :  26.90   3rd Qu.:  28.00  Max.   :736.00 std : 50.09

def get_user_number_of_reviews_dict( review_dict ):
    user_review_dict = {}
    for value in review_dict.values():
        for key, value in value.items():
                     if key in user_review_dict:
                         user_review_dict[key] += 1
                     else:
                         user_review_dict[key] = 1
    print(len(user_review_dict))
    return(user_review_dict)

def get_user_rating_distribution(user_review_dict):
    user_review_list = user_review_dict.values()
    ser = pd.Series(user_review_list)
    print(ser.describe())

    # Original: Min.   :  1.000   1st Qu.:  1.000   Median :  1.000   Mean   :  3.16   3rd Qu.:  3.000   Max.   :575.000 std : 8.762357
    # Final :   Min.   :  10.00    1st Qu.:  12.00    Median :  15.00    Mean   : 24.74   3rd Qu.: 24.00    Max.   :575.00 std : 31.597

def get_final_dataset(review_dict):
    final_review_dict = {}
    user_rating_dict = get_user_number_of_reviews_dict( review_dict )
    review_count = 0
    for restaurant, value in review_dict.items():
        for reviewer, rating in value.items():
                     if reviewer in user_rating_dict and user_rating_dict[reviewer] >= 20:
                         review_count += 1
                         if restaurant not in final_review_dict: final_review_dict[restaurant] = { reviewer : rating}
                         else:
                             final_review_dict[restaurant][reviewer] = rating

    print(len(final_review_dict))
    print(review_count)
    return(final_review_dict)   # restaurants:4825  users:5247 reviews:129811


def get_original_user_friends_dictionary(user_file):
    original_user_friends_dict = {}
    user_info = open(user_file)
    for line in user_info:
        user = json.loads(line)
        if user["user_id"] and user["friends"]:
            original_user_friends_dict[user["user_id"]] = user["friends"]
    return(original_user_friends_dict)


def get_final_friends_dict(final_review_dict, user_file):
    friends_list_dict = {}
    original_friends_dict = get_original_user_friends_dictionary(user_file)
    user_rating_dict = get_user_number_of_reviews_dict(final_review_dict)
    for user in user_rating_dict.keys():
        if original_friends_dict.has_key(user):
            for friends in original_friends_dict[user]:
                if friends in user_rating_dict and user not in friends_list_dict:
                    friends_list_dict[user] = [friends]
                elif friends in user_rating_dict and user in friends_list_dict:
                    friends_list_dict[user].append(friends)
    print(len(friends_list_dict))
    return friends_list_dict # 10689 have friends

def get_final_friends_distribution(final_review_dict, user_file):
    friends_list_dict = get_final_friends_dict(final_review_dict, user_file)
    friends_number_set = []
    for value in friends_list_dict.values():
        friends_number_set.append(len(value))
    ser = pd.Series(friends_number_set)
    print(ser.describe())

    #  Min.   :   1.00   1st Qu.:   2.00   Median :   6.00   Mean   :  21.82   3rd Qu.:  18.00   Max.   :1478.00 std : 54.932842


def create_json_restaurant_data(final_review_dict, business_file):
    business_data = open(business_file)
    with io.open("business_data.json", "w", encoding="utf-8") as outfile:
        for line in business_data:
            business = json.loads(line)
            if  business.has_key("business_id") and business["business_id"].encode('utf-8') in final_review_dict:
                business_data = { "business_id" : business["business_id"],
                                  "name" : business["name"],
                                  "full_address" : business["full_address"],
                                  "city" : business["city"],
                                  "state" : business["state"],
                                  "latitude" : business["latitude"],
                                  "longitude" : business["longitude"],
                                  "stars" : business["stars"],
                                  "categories": business["categories"]}
                outfile.write(unicode(json.dumps(business_data, outfile, ensure_ascii=False)) + '\n')


def get_restaurant_cuisine(final_review_dict, business_file):
    restaurant_cuisine_dict = {}
    cuisine_list = ['Afghan', 'African', 'American (New)', 'American (Traditional)', 'Arabian', 'Argentine',
        'Armenian', 'Asian Fusion', 'Asturian' , 'Australian' ,'Austrian', 'Baguettes' , 'Bangladeshi' ,'Barbeque' ,
        'Basque' ,'Bavarian' ,'Beer Garden', 'Beisl' ,'Belgian','Flemish' ,'Bistros', 'Black Sea' ,'Brasseries' ,
        'Brazilian' ,'Breakfast & Brunch', 'British', 'Buffets', 'Bulgarian' ,'Burgers' ,'Burmese' ,'Cafes' ,'Cafeteria' ,
        'Cajun/Creole','Cambodian' ,'Canadian' ,'Canteen' ,'Caribbean' ,'Dominican' ,'Haitian' ,'Puerto Rican' ,
        'Trinidadian' , 'Catalan' ,'Chech' ,'Cheesesteaks' , 'Chicken Wings','Chilean' ,'Chinese' ,'Cantonese' ,
        'Congee' ,'Dim Sum' ,'Hakka' ,'Henghwa' ,'Hunan','Pekinese' ,'Shanghainese' ,'Szechuan' ,'Comfort Food',
        'Corsican' ,'Creperies' ,'Cuban' ,'Curry Sausage', 'Cypriot' ,'Czech' ,'Czech/Slovakian' ,'Danish' ,'Delis',
        'Diners', 'Dumplings' ,'Eastern European' ,'Ethiopian' ,'Fast Food', 'Filipino' ,'Fischbroetchen' ,'Fish & Chips' ,
        'Fondue' ,'Food Court' ,'Food Stands', 'French' , 'Alsatian', 'Auvergnat' , 'Berrichon' ,'Bourguignon' ,
        'Nicoise' ,'Provencal' ,'French Southwest' ,'Galician' ,'Gastropubs' ,'Georgian' ,'German' ,
        'Eastern German', 'Gluten-Free' ,'Greek' ,'Hawaiian' ,'Heuriger' ,'Himalayan/Nepalese','Hong Kong Style Cafe' ,
        'Hot Dogs' ,'Hot Pot' ,'Hungarian' ,'Indian' ,'Indonesian', 'International' ,'Irish' ,'Island Pub' ,
        'Israeli','Italian' ,'Abruzzese' , 'Altoatesine' ,'Apulian' ,'Calabrian' ,'Cucina campana' ,'Emilian' ,
        'Friulan', 'Ligurian' ,'Lumbard' ,'Napoletana' , 'Piemonte' ,'Roman' ,'Sardinian' ,'Sicilian','Tuscan' ,
        'Venetian' ,'Japanese', 'Blowfish' ,'Conveyor Belt Sushi' ,'Donburi' , 'Gyudon' ,'Oyakodon' ,'Hand Rolls' ,
        'Horumon' ,'Izakaya' ,'Japanese Curry','Kaiseki' ,'Kushikatsu' ,'Oden' ,'Okinawan' , 'Okonomiyaki' ,
         'Onigiri' ,'Ramen' ,'Robatayaki','Soba' ,'Sukiyaki' ,'Takoyaki' ,'Tempura' ,'Teppanyaki' ,'Tonkatsu' ,
         'Udon' ,'Unagi' ,'Western Style Japanese Food' ,'Yakiniku' ,'Yakitori' ,'Jewish ','Kebab ','Korean' ,
         'Kosher' ,'Kurdish' ,'Laos', 'Laotian' ,'Latin American' ,'Colombian' ,'Salvadoran','Venezuelan' ,
         'Live/Raw Food' ,'Lyonnais' ,'Malaysian' ,'Mamak' , 'Nyonya' ,'Meatballs' ,'Mediterranean' ,'Falafel' ,
         'Mexican' ,'Eastern Mexican' ,'Jaliscan' ,'Northern Mexican' ,'Oaxacan' ,
         'Pueblan' ,'Tacos' ,'Tamales' ,'Yucatan' ,'Middle Eastern', 'Egyptian' , 'Lebanese' ,'Milk Bars' ,
         'Modern Australian' ,'Modern European','Mongolian' ,'Moroccan' ,'New Zealand' ,'Night Food' ,'Norcinerie' ,
         'Open Sandwiches' ,'Oriental' ,'Pakistani' ,'Parent Cafes' ,'Parma' ,'Persian/Iranian' ,'Peruvian' ,'Pita' ,'Pizza' ,
         'Polish' ,'Pierogis' ,'Portuguese' , 'Alentejo' ,'Algarve' , 'Azores' ,'Beira' ,'Fado Houses' ,
         'Madeira','Potatoes' ,'Poutineries' ,'Pub Food', 'Rice' ,'Romanian' , 'Rotisserie Chicken' ,'Rumanian' ,
         'Russian' ,'Salad' ,'Sandwiches' ,'Scandinavian' ,'Scottish' ,'Seafood' ,'Serbo Croatian' ,
         'Signature Cuisine','Singaporean' ,'Slovakian' ,'Soul Food' ,'Soup' ,'Southern' ,'Spanish',
         'Arroceria / Paella', 'Steakhouses' ,'Sushi Bars' ,'Swabian' ,'Swedish' ,'Swiss Food','Tabernas' ,
         'Taiwanese' ,'Tapas Bars' ,'Tapas/Small Plates', 'Tex-Mex' ,'Thai','Traditional Norwegian' ,
         'Traditional Swedish' ,'Trattorie' ,'Turkish','Chee Kufta' ,'Gozleme' , 'Turkish Ravioli' ,'Ukrainian' ,
         'Uzbek' ,'Vegan' ,'Vegetarian','Venison' ,'Vietnamese' ,'Wok' ,'Wraps' ,'Yugoslav' ]
    cuisine_set = set(cuisine_list)
    business_data = open(business_file)
    with io.open("business_data.json", "w", encoding="utf-8") as outfile:
        for line in business_data:
            business = json.loads(line)
            if  business.has_key("business_id") and business["business_id"].encode('utf-8') in final_review_dict:
                business_categories = [category.encode('utf-8').lower() for category in business["categories"]]
                cuisine_categories = [category.encode('utf-8').lower() for category in cuisine_list]
                for category in business_categories:
                    if category in cuisine_categories:
                        restaurant_cuisine_dict[business["business_id"].encode('utf-8')] = category
                if business["business_id"].encode('utf-8') not in restaurant_cuisine_dict:
                        restaurant_cuisine_dict[business["business_id"].encode('utf-8')] = ""
    return restaurant_cuisine_dict

def create_json_restaurant_data_with_cuisine(final_review_dict, business_file, restaurant_cuisine_dict):
    business_data = open(business_file)
    with io.open("restaurant_data.json", "w", encoding="utf-8") as outfile:
        for line in business_data:
            business = json.loads(line)
            if  business.has_key("business_id") and business["business_id"].encode('utf-8') in final_review_dict:
                business_data = { "business_id" : business["business_id"],
                                  "name" : business["name"],
                                  "full_address" : business["full_address"],
                                  "city" : business["city"],
                                  "state" : business["state"],
                                  "latitude" : business["latitude"],
                                  "longitude" : business["longitude"],
                                  "stars" : business["stars"],
                                  "cuisine": restaurant_cuisine_dict[business["business_id"]]}
                outfile.write(unicode(json.dumps(business_data, outfile, ensure_ascii=False)) + '\n')

def create_csv_restaurant_data_with_cuisine(final_review_dict, business_file, restaurant_cuisine_dict):
    business_data = open(business_file)
    col_names = ["item_id", "name", "cuisine"]
    item_data = []

    for line in business_data:
        business = json.loads(line)
        if  business.has_key("business_id") and business["business_id"].encode('utf-8') in final_review_dict:
          item_data.append([business["business_id"], business["name"], restaurant_cuisine_dict[business["business_id"]]])
    dataF = pd.DataFrame(item_data, columns = col_names)
    dataF.to_csv("item_data.csv", encoding='utf-8', index = False)


def create_csv_restaurant_data_with_url(final_review_dict, business_file, restaurant_cuisine_dict, restaurant_url_dict):
    business_data = open(business_file)
    col_names = ["item_id", "name", "cuisine", "full_address", "url"]
    item_data = []

    for line in business_data:
        business = json.loads(line)
        if  business.has_key("business_id") and business["business_id"].encode('utf-8') in final_review_dict:
          if restaurant_url_dict.has_key(business["business_id"]):
            url = restaurant_url_dict[business["business_id"]]
          else:
            url = None
          item_data.append([business["business_id"],
            business["name"],
            restaurant_cuisine_dict[business["business_id"]],
            business['full_address'],
            url])
    dataF = pd.DataFrame(item_data, columns = col_names)
    print len(dataF)
    dataF.to_csv("item_data.csv", encoding='utf-8', index = False)


def create_restaurant_url_dict(url_file):
    url_data = pd.read_csv(url_file)
    restaurant_url_dict = {}
    for row in url_data.iterrows():
        restaurant_url_dict[row[1]['item_id']] = row[1]['url']
    return restaurant_url_dict

def find_missing_urls(business_file, restaurant_url_dict):
  business_data = open(business_file)
  with io.open("missing_url.json", "w", encoding="utf-8") as outfile:
        for line in business_data:
            business = json.loads(line)
            if business["business_id"] not in restaurant_url_dict:
              missing = { "item_id" : business["business_id"],
                          "name" : business["name"]}
              outfile.write(unicode(json.dumps(missing, outfile)) + '\n')


def create_matrix_for_collaborative_filtering(final_review_dict):
    restaurant_review_matrix = pd.DataFrame(final_review_dict)
    df = pd.DataFrame(restaurant_review_matrix).T.fillna(0)
    df.to_csv("restaurant_review.csv", encoding='utf-8')

def create_restaurant_name_dict(business_file):
    restaurant_name_dict = {}
    business_data = open(business_file)
    for line in business_data:
        business = json.loads(line)
        restaurant_name_dict[business["business_id"].encode('utf-8')] = business["name"].encode('utf-8')
    return restaurant_name_dict


def create_data_for_use_in_GraphLab(final_review_dict, restaurant_name_dict):
    data = []
    col_names = "restaurant_id", "user", "restaurant", "rating"
    for restaurant, value in final_review_dict.items():
        for user, rating in value.items():
            col_values = [ restaurant, user, restaurant_name_dict[restaurant], rating]
            data.append(col_values)
    print data[25]
    dataF = pd.DataFrame(data, columns = col_names)
    plt.hist(dataF["rating"])
    plt.xlabel("Rating")
    plt.show()
    #dataF.to_csv("restaurant_data.csv", encoding='utf-8')


def create_data_for_use_in_GraphLab_new(final_review_dict, restaurant_name_dict):
    data = []
    col_names = "id", "user", "rating"
    for restaurant, value in final_review_dict.items():
        for user, rating in value.items():
            col_values = [ restaurant, user, rating]
            data.append(col_values)
    print data[25]
    dataF = pd.DataFrame(data, columns = col_names)
    dataF.to_csv("restaurant_data_new.csv", encoding='utf-8', index = False)

def create_friends_data(friends_list_dict):
    friends_data = {}

    col_names = ["user", "friend"]
    for user, friends_list in friends_list_dict.items():
        for friend in friends_list:
            if (user, friend) and (friend, user) not in friends_data:
                col_values = (user, friend)
                friends_data[col_values] = 1
    print len(friends_data) # 116622 set of friendships
    dataF = pd.DataFrame(friends_data.keys(), columns = col_names)
    print dataF.head(3)
    dataF.to_csv("friends_data.csv", encoding = 'utf-8')
    return friends_data


def create_friends_ratings_dict(final_review_dict, friends_data):
    friends_rating_dict = {}
    for (friend1, friend2) in friends_data:
        for restaurant, user_ratings in final_review_dict.items():
            if friend1 in user_ratings and friend2 in user_ratings:
                if (friend1, friend2) in friends_rating_dict:
                    friends_rating_dict[(friend1, friend2)].append((user_ratings[friend1], user_ratings[friend2]))
                else:
                    friends_rating_dict[(friend1, friend2)] = [(user_ratings[friend1], user_ratings[friend2])]
    print len(friends_rating_dict) # 58123 set of friends have rated same restaurants
    return friends_rating_dict


def create_friends_similarity_dict(friends_rating_dict):
    friends_similarity_dict = {}
    for friends, ratings in friends_rating_dict.items():
        print ratings
        friend1ratings, friend2ratings = [], []
        for (rating1, rating2) in ratings:
            friend1ratings.append(rating1)
            friend2ratings.append(rating2)
        print friend1ratings, friend2ratings
        similarity = np.corrcoef(friend1ratings,friend2ratings)[0,1]
        print similarity
        friends_similarity_dict[friends] = similarity
    print len(friends_similarity_dict)

def find_restaurant_id_by_cuisine(restaurant_file, cuisine):
  restaurant_data = open(restaurant_file)
  restaurant_list_for_cuisine = {}
  for line in restaurant_data:
    restaurant = json.loads(line)
    if restaurant["cuisine"] == cuisine:
      restaurant_list_for_cuisine[restaurant["business_id"].encode('utf-8')] = restaurant["name"].encode('utf-8')
  pickle.dump(restaurant_list_for_cuisine, open( "chinese_restaurants" + '.pickle','wb'))
  print restaurant_list_for_cuisine.items()

def create_celebrity_restaurant_set(restaurant_file):
    celebrity_chef_restaurant_list = ["4uGHPY-OpJN08CabtTAvNg", "wfofFm3AqtyK_ujNQ893mQ",
    "Iyy4pDmnKTZkAorzclO4Eg", "nEY3mwbpAJlQ5FOQ-F4Giw", "ZNdsRbGeOfrYYPRl6AziCQ", "qXG8IlKuvy5k9fJ3y2gLgg",
    "_5k83wy9_5NpErw7Ecgt3g","Pz7SWZQhxL6ZbhL9jE2NTA", "3w5gd4EuSc75UKYMJiNUPA", "a3HmtiW3WzUvKxWy9Fezkg",
    "uYKwS-biARKgBkk5rY_PaQ", "Ieuv-XET6SR_qIscZzgD-A"]

    restaurant_list = {}
    restaurant_data = open(restaurant_file)
    for line in restaurant_data:
      restaurant = json.loads(line)
      if restaurant["business_id"] in celebrity_chef_restaurant_list:
        restaurant_list[restaurant["business_id"].encode('utf-8')] = restaurant["name"].encode('utf-8')
    pickle.dump(restaurant_list, open( "celebrity_chef_restaurant" + '.pickle','wb'))
    print restaurant_list.items()

def create_example_json_data(restaurant_file, dataset):
    restaurant_data = open(restaurant_file)
    with io.open("example_1.json", "w", encoding="utf-8") as outfile:
        for line in restaurant_data:
            restaurant = json.loads(line)
            if restaurant["name"].encode('utf-8') in dataset:
              business_data = { "item_id" : restaurant["business_id"].encode('utf-8'),
                                  "name" : restaurant["name"].encode('utf-8'),
                                  "cuisine": restaurant["cuisine"].encode('utf-8'),
                                  "rating" : 5}
              outfile.write(unicode(json.dumps(business_data, outfile)) + '\n')

def main():
    #sent_file = open(sys.argv[1])
    business_file = "yelp_academic_dataset_business.json"
    categories_to_look_for = ["restaurants", "restaurant", "cafe", "bar"]
    city_to_look_for = "las vegas"
    review_file = "yelp_academic_dataset_review.json"
    user_file = "yelp_academic_dataset_user.json"
    restaurant_file = "restaurant_data.json"
    url_file = "restaurant_url_data.csv"

    #explore_restaurant_data(business_file)
    #create_restaurant_set(business_file, city_to_look_for, categories_to_look_for)
    review_dict = create_review_dict(review_file, business_file, city_to_look_for, categories_to_look_for)
    #get_restaurant_rating_distribution(review_dict)
    #user_review_dict = get_user_number_of_reviews_dict(review_dict)
    #get_user_rating_distribution(user_review_dict)
    final_review_dict = get_final_dataset(review_dict)
    get_restaurant_rating_distribution(final_review_dict)
    user_review_dict = get_user_number_of_reviews_dict(final_review_dict)
    get_user_rating_distribution(user_review_dict)
    #get_final_friends_distribution(final_review_dict, user_file)
    #create_json_restaurant_data(final_review_dict, business_file)
    #create_json_restaurant_data_short(final_review_dict, business_file)
    #num_of_restaurants = len(final_review_dict)
    #num_of_users = len(user_review_dict)
    #create_matrix_for_collaborative_filtering(final_review_dict)
    #data = np.genfromtxt("restaurant_review.csv", delimiter = ",")
    restaurant_name_dict = create_restaurant_name_dict(business_file)
    restaurant_cuisine_dict = get_restaurant_cuisine(final_review_dict, business_file)
    #create_json_restaurant_data_with_cuisine(final_review_dict, business_file, restaurant_cuisine_dict)
    create_data_for_use_in_GraphLab(final_review_dict, restaurant_name_dict)
    #get_max_restaurant_rating(final_review_dict, restaurant_name_dict)
    #friends_list_dict = get_final_friends_dict(final_review_dict, user_file)
    #friends_data = create_friends_data(friends_list_dict)
    #friends_rating_dict = create_friends_ratings_dict(final_review_dict, friends_data)
    #create_friends_similarity_dict(friends_rating_dict)
    #create_friends_data(friends_list_dict)
    #print data[1,:]
    #print(type(data))
    #print sum((data>0).sum())
    #create_data_for_use_in_GraphLab_new(final_review_dict, restaurant_name_dict)
    #find_restaurant_id_by_cuisine(restaurant_file, "chinese")
    #create_csv_restaurant_data_with_cuisine(final_review_dict, business_file, restaurant_cuisine_dict)
    #restaurant_url_dict = create_restaurant_url_dict(url_file)
    #create_csv_restaurant_data_with_cuisine_url(final_review_dict, business_file, restaurant_cuisine_dict, restaurant_url_dict)
    #find_missing_urls(restaurant_file, restaurant_url_dict)

    #create_celebrity_restaurant_set(restaurant_file)
    dataset_1 = ['Koji Restaurant', 'Rice To-Go', 'Dragon Noodle Co.', 'Great China', 'New China Buffet',
    'Yummy House', 'Pho Hoang', "Emperor's Garden", 'Ichiban', "Ming's Table", 'Manchu Wok',
    'Little Dumpling Chinese & Thai Cuisine', "Lillie's Asian Cuisine", 'Soyo Korean Barstaurant',
   'Ports O Call Buffet']

    dataset_2 = ['Moko Tapas Bar', 'Taqueria Los Parados', 'Alex', 'Snow Ono Shave Ice',
   'Guy Savoy', 'Joel Robuchon', 'Weeziana Gumbo & More', 'In-N-Out Burger', 'Kabuto',
   'Tacos El Gordo', "Mama Maria's Mexican Restaurant", 'Baguette Cafe', "L'Atelier de Joel Robuchon",
   'Great Buns Bakery', 'the Goodwich', "Lulu's On The Move", 'Soho Japanese Restaurant']

    dataset_3 = ['Nobhill Tavern by Michael Mina', 'Fukumimi Ramen',
   'Fleur by Hubert Keller', '\xc3\xa9 by Jos\xc3\xa9 Andr\xc3\xa9s', 'Raku',
   "Slidin' Thru", 'Stack Restaurant & Bar', 'Foundation Room', 'Michael Mina',
   'ARIA Cafe', 'Shibuya', 'Palm Restaurant', 'RE Tapas', 'Bouchon',
   'Rincon De Buenos Aires', 'Taqueria Los Parados', 'Sedona Lounge', 'Bacio', 'Sushi Hana']

    #create_example_json_data(restaurant_file, dataset_1)


if __name__ == '__main__':
    main()
