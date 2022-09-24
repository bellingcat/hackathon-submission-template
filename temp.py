import plotly_express as px
import pandas
import networkx as nx

edge_df = pandas.read_csv(r'/home/timo/random_coding/Bellingcat Hackathon/edge_list.csv', header= None)
info_df = pandas.read_csv(r'/home/timo/random_coding/Bellingcat Hackathon/user_info.csv')

#def bar_plot_followers(info_df):

follower_df = info_df.sort_values('#followers')
follower_df = follower_df.tail(20)

fig_follower = px.bar(follower_df, x='Unnamed: 0',y='#followers',
                      color= '#followers', color_continuous_scale= 'deep',
             labels={
                 "Unnamed: 0" : "username",
                 "#followers" : "number of followers"},
                      )
fig_follower.update_traces(hovertemplate='username: %{x}'+'<br>followers: %{y}')
fig_follower.update_layout(title_text= "accounts with most followers", title_x= 0.5)
fig_follower.update_layout({
'plot_bgcolor': 'rgba(0, 0, 0, 0)',
'paper_bgcolor': 'rgba(0, 0, 0, 0)',
})
#fig_follower.write_html("accounts_with_most_followers.html")

#def bar_plot_posts(info_df):
post_df = info_df.sort_values('#posts')
post_df = post_df.tail(20)

fig_post = px.bar(post_df, x='Unnamed: 0', y='#posts',
                  color= '#posts', color_continuous_scale= 'deep',
             labels={
                 "Unnamed: 0" : "username",
                 "#posts" : "number of posts"})
fig_post.update_traces(hovertemplate='username: %{x}'+'<br>posts: %{y}')
fig_post.update_layout(title_text= "accounts with most posts", title_x= 0.5)
fig_post.update_layout({
'plot_bgcolor': 'rgba(0, 0, 0, 0)',
'paper_bgcolor': 'rgba(0, 0, 0, 0)',
})

#fig_post.write_html("accounts_with_most_posts.html")

#def analysis_plot(info_df) :
g = nx.from_pandas_edgelist(df = edge_df, source = 0, target = 1) #unsure if we will need this in the final version
nusers = info_df.shape[0]
degree_centrality = nx.degree_centrality(g)

print(degree_centrality)



#centrality? most acive user? density? number of  (meaningful) clusters?