import sys
import json
import csv
from snscrape.base import ScraperException
import snscrape.modules.twitter as st
import multiprocessing
import itertools
import pandas as pd
import datetime
from pathlib import Path
import os



def get_user_tweets(user: str, n_tweets:int):


    
    sns_user = st.TwitterUserScraper(user)
    try:
        sns_generator = sns_user.get_items()
    except ScraperException:
        return None
    tweets = itertools.islice(sns_generator, n_tweets)

    tweet_ids = map(lambda x: x.id, tweets)

    raw_mentions = map(lambda x: x.mentionedUsers, tweets)
    mentions = []
    try:
        for i in raw_mentions:
            if i and i[0]:
                mentions.append(i[0].username)
    except ScraperException:
        return None
    try:
        user_result = sns_user._get_entity()

    except KeyError:
        user_info = {"potentially_banned": True}
    else:
        if user_result:
            user_info = {"id": user_result.id,
                         "display name": user_result.displayname,
                         "description": user_result.description,
                         "verified": user_result.verified,
                         "potentially_banned": False,
                         "#followers": user_result.followersCount,
                         "#posts": user_result.statusesCount,
                         "#friends": user_result.friendsCount,
                         "#favourites": user_result.favouritesCount,
                         "location": user_result.location
                         }
        else:
            user_info = {"potentially_banned": True}

    return (list(tweet_ids), mentions, user_info)




def iteration(args):
    """
    gets tweets ids and mentions from one user
    adds mentions to new_users
    goes through all tweets and adds all mentions from there to new_users
    returns the set of new users

    user: name of the user

    Returns: set of all newly found users
    """

    user, n_tweets = args[0], args[1]
    dict_update = get_user_tweets(user, n_tweets)

    if not dict_update:
        return None

    new_users = dict_update[1]

    return (new_users, (user, dict_update))


def start_from_user(user: str, max_it: int = 1, n_tweets: int = 100):

    user_dict = {}

    visited_users = set(user)
    
    result = iteration((user, n_tweets))
    new_users = set(result[0])
    user_dict[user] = result[1][1]
    users_to_update_with = set()

    i = 0
    pool = multiprocessing.Pool(processes=12)
    while i < max_it:

        i += 1

        new_users = new_users.difference(visited_users)

        data = [(sub_user, n_tweets) for sub_user in new_users if sub_user]

        result = pool.map(iteration, data)

        visited_users.update(new_users)
        
        users_to_update_with = filter(None, map(lambda x: x[0] if x else None, result))
        dict_updates = filter(None, map(lambda x: x[1] if x else None, result))

        for user_name, content in dict_updates:
            user_dict[user_name] = content

        new_users = set(
            [user for user_list in users_to_update_with for user in user_list if user])
        users_to_update_with = set()

    return user_dict


def main(start_user:str, depth:int, num_tweets:int, project_name:str='Project_name', save:bool=True)->tuple:
    """Main wrapper for using snscrape; retrieves data, stores the edge and user data 
    inside dataframes and jsons. Returns a tuple with the folder path to where the 
    data was saved and the dataframe itself

    Args:
        start_user (str): _description_
        depth (int): _description_
        num_tweets (int): _description_
        project_name (str, optional): _description_. Defaults to 'Project_name'.

    Returns:
        tuple: path to output folder, dataframe
    """    

    edges = []
    user_info = {}
    
    global n_tweets
    n_tweets = num_tweets
    print('Getting data via snscrape ...')
    result_dict = start_from_user(start_user, depth, n_tweets)
    print('Searching from user: ...', start_user)
    for user, content in result_dict.items():
        for mentioned in content[1]:
            print('\tMentioned: ', mentioned)
            edges.append((user,mentioned))


    edges_set = set(edges)
    out_edges = []

    print('Iterating over edges: ...')
    i=1
    for edge in edges:
        if (edge[1], edge[0]) in edges_set:
            out_edges.append(edge)
            try:
                user_info[edge[0]] = result_dict[edge[0]][2]
                print(i)
                i+=1
            except KeyError:
                continue

    edge_attr_dict = {}
    for edge in out_edges:
        edge_attr_dict[str(edge)] = edges.count(edge)
        

    
    user_info_pd = pd.DataFrame.from_dict(user_info, orient="index")
    user_info_pd.to_csv("user_attributes.csv")

    

    data_path = Path(f"Data/{project_name}/")
    day = datetime.datetime.now().date().isoformat() + "_"
    time = str(datetime.datetime.now().hour)+ "-" + str(datetime.datetime.now().minute)
    

    run_path = data_path / (day + time)
    print('Saving data inside ', run_path)
    os.makedirs(run_path)
    
    run_params_dict = {"start user" : start_user,
                       "recursion depth" : depth,
                       "number of tweets searched per user": n_tweets}


    if save:
        save_query_results(run_path, run_params_dict, out_edges, user_info, edge_attr_dict)

    return run_path, run_params_dict, out_edges, user_info, edge_attr_dict

def save_query_results(run_path:str, run_params_dict:dict, out_edges, user_info, edge_attr_dict):

    with open((run_path / 'run_info.json'), 'w') as handle:
        json.dump(run_params_dict, handle)
    
    with open((run_path / 'edge_list.csv'), 'w') as handle:
        writer = csv.writer(handle)
        writer.writerows(out_edges)

    with open((run_path / 'edge_list.json'), 'w') as handle:
        json.dump(out_edges, handle)

    with open((run_path / 'user_attributes.json'), 'w') as handle:
        json.dump(user_info, handle)

    with open((run_path / 'edge_attributes.json'), 'w') as handle:
        json.dump(edge_attr_dict, handle)


if __name__ == "__main__":


    start_user = sys.argv[1]
    depth = int(sys.argv[2])
    n_tweets = int(sys.argv[3])

    main(start_user, depth, n_tweets)

