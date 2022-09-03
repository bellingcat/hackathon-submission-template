import subprocess
import json
from typing import List, Tuple, Set, Dict
import csv
from tqdm import tqdm
import snscrape.modules.twitter as st
import multiprocessing



# def iterate(user, edges):
#     mentions = twitter_user(user)
#    for i in mentions:
#         edges.append((user, i))
#     return mentions


# edges = []

# mentions = iterate(start_user, edges)
# visited_users = set(mentions)
# for i in mentions:
#     newer_mentions = iterate(i, edges)

#     for x in tqdm(newer_mentions):
#         print("level2")
#         if x not in visited_users:
#             even_newer_mentions = iterate(x, edges)

#     visited_users.update(set(newer_mentions))


def get_user_tweets(user: str) -> Tuple[List[int], List[str]]:



    print(user)
    tweets = list(st.TwitterUserScraper(user).get_items())

    tweet_ids = map(lambda x: x.id, tweets)

    raw_mentions = map(lambda x: x.mentionedUsers, tweets)
    mentions = []
    for i in raw_mentions:
        if i and i[0]:
            mentions.append(i[0].username)

    return (list(tweet_ids), mentions)


def get_replies(tweet: int) -> List[str]:

    return []


# def iteration(user: str, user_dict: Dict[str, Tuple[List[int], List[str]]]) -> Set[str]:
def iteration(args):
    """
    gets tweets ids and mentions from one user
    adds mentions to new_users
    goes through all tweets and adds all mentions from there to new_users
    returns the set of new users

    user: name of the user
    user_dict: central storage of collected data

    Returns: set of all newly found users
    """
    user, user_dict = args[0], args[1]
    dict_update = get_user_tweets(user)
    new_users = dict_update[1]


    return (set(new_users), (user, dict_update))


def start_from_user(user: str, max_it: int = 1):

    # user_dict = { "user_id" : ( tweet_ids,  mentions)}
    user_dict = {}

    visited_users = set(user)
    
    result = iteration((user, user_dict))
    new_users = result[0]
    user_dict[user] = result[1][1]
    users_to_update_with = set()

    i = 0
    pool = multiprocessing.Pool(processes=8)
    while i < max_it:
        i += 1
        print(f"Depth {i}\n lengtht of user dict: {len(user_dict.keys())}")

        new_users = new_users.difference(visited_users)

        data = [(sub_user, user_dict) for sub_user in new_users]

        result = pool.map(iteration, data)

        visited_users.update(new_users)
        
        users_to_update_with = map(lambda x: x[0], result)
        dict_updates = map(lambda x: x[1], result)
        for user_name, content in dict_updates:
            user_dict[user_name] = content
            
        
        
        new_users = users_to_update_with
        users_to_update_with = set()

    return user_dict


start_user = "JbRuhiges"
edges = []
result_dict = start_from_user(start_user)
for user, content in result_dict.items():
    for mentioned in content[1]:
        edges.append((user,mentioned))
    

with open('output.csv', 'w') as file:
    writer = csv.writer(file)
    writer.writerows(edges)
