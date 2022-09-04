#====================
#BELLINGCAT NETWORK ANALYSIS HACKATHON
#===================
#----general preparations----
list.of.packages <- c("statnet", "network", "dplyr", "igraph" , "plotly", "intergraph",
                      "htmlwidgets")
new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
if(length(new.packages)) install.packages(new.packages)

library(statnet)
library(network)
library(dplyr)
library(igraph)
library(plotly)
library(intergraph)


#----data import----
#the edgelist of interactions
usr_names <- read.csv("/home/td/random_coding/Bellingcat Hackathon/edge_list.csv", header = F)

#also replace the path from my private machine with some general path to the data
#the attributes of the Twitter accounts on the edgelist
usr_attr <-read.csv("/home/td/random_coding/Bellingcat Hackathon/user_info.csv", header = T)

#----data cleaning and preparation----
#make sure the edgelists and the file with the nodal attributes are in the same
#order so the matching process is not messed up
#this step only has to be done for this specific dataset, to be eliminated later.
#TTboard2011$...2 <- as.character(TTboard2011$...2)
usr_names <- na.omit(usr_names)
usr_attr <- na.omit(usr_attr)
usr_attr$verified <-dplyr::recode(usr_attr$verified, "False" = "not verified",
                                  "True" = "verified")
usr_attr['first'] <- 5
usr_attr$first[1] <- 20

#----creating the network----
#conversion from edgelist into network in statnet
usr_names <- transform(usr_names,                          # Create ID by group
                      ID1 = as.numeric(factor(V1)))
usr_names <- transform(usr_names,                          # Create ID by group
                          ID2 = as.numeric(factor(V2)))
usr_names <- `colnames<-`(usr_names, c("X", "V2", "ID1", "ID2"))
usr_edgelist <- select(usr_names, "ID1", "ID2")
usr_net_matrix <- as.matrix(usr_edgelist, mode = "undirected", weighted = T)
usr_net <- network(usr_net_matrix, vertex.attr = usr_attr, 
                   vertex.attrnames = colnames(usr_attr), directed = F, 
                   hyper = F, loops = T, 
                   multiple = F, bipartite = F)
usr_net_matrix <- as.matrix(usr_net, mode = "undirected", weighted = T)
#explanation of the code: user_edgelist is a data.frame when importing as .csv. 
#If converted to a network from a data.frame it creates parallel edges. 
#If imported as a weighted matrix however, it creates weighted edges.
usr_attr$label <- paste(usr_attr$X, ",", usr_attr$X.followers, "followers", ",",
                        usr_attr$verified)

#----interactive visualizations----
#1. of the network
#reading the graph file
G <- asIgraph(usr_net)
G <- set_vertex_attr(G, "label", value = c(usr_attr$label))
G <- set_vertex_attr(G, "verified", value = c(usr_attr$verified))
G <- set_vertex_attr(G, "first",value = c(usr_attr$first))
G <- upgrade_graph(G)
L <- layout.graphopt(G)
edge_shapes <- list()
#create vertices and edges
V(G)$color <- ifelse(V(G)$verified == "verified", "blue", "green")
vs <- V(G)
es <- as.data.frame(get.edgelist(G))
Nv <- length(vs)
Ne <- length(es[1]$V1)
#creating the nodes
Xn <- L[,1]
Yn <- L[,2]
network <- plot_ly(x = ~Xn, y = ~Yn, mode = "markers", opacity= 3, marker = list(size = 7.5, family = "Times New Roman")
                  , text = vs$label , hoverinfo = "text", color = vs$color)
#creating the edges
for(i in 1:Ne) {
  v0 <- es[i,]$V1
  v1 <- es[i,]$V2
  
  edge_shape = list(
    type = "line",
    line = list(color = "#030303", width = 0.3),
    x0 = Xn[v0],
    y0 = Yn[v0],
    x1 = Xn[v1],
    y1 = Yn[v1]
  )
  edge_shapes[[i]] <- edge_shape
}
#creating the network
axis <- list(title = "", showgrid = FALSE, showticklabels = FALSE, zeroline = FALSE)
fig <- layout(
  network,
  title = 'user network',
  shapes = edge_shapes,
  xaxis = axis,
  yaxis = axis, 
  showlegend = F
)
fig <- fig %>%
  add_trace(
    x = Xn,
    y = Yn,
    marker = list(
      size = vs$first
      ))

htmlwidgets::saveWidget(fig, file = "user_network.html")

#2. interactive barplots and histograms
#histogram of followers
hist_fig <-usr_attr %>%
  filter(!is.na(X.followers)) %>%
  arrange(desc(X.followers)) %>%
  slice(1:20)

hist_fig <- plot_ly(hist_fig, x = ~X, y = ~X.followers) %>%
layout(title = '20 most followed accounts', xaxis = list(title = 'account name'), 
       yaxis = list(title = 'number of followers'))
htmlwidgets::saveWidget(hist_fig, file = "most_followed_accounts.html")

#histogram of posts
hist_posts <-usr_attr %>%
  filter(!is.na(X.posts)) %>%
  arrange(desc(X.posts)) %>%
  slice(1:20)

hist_posts <- plot_ly(hist_posts, x = ~X, y = ~X.posts) %>%
  layout(title = '20 accounts with the most posts', xaxis = list(title = 'username'), 
         yaxis = list(title = 'number of posts'))
htmlwidgets::saveWidget(hist_posts, file = "accounts_with_most_posts.html")

#----descriptive statistics----
nusers <- length(unique(usr_edgelist[,2])) #number of users in the network (check if this actually counts the users)
deg <- igraph::graph_from_data_frame(usr_edgelist)
deg <- degree(deg)
deg <- as.data.frame(table(deg))
deg <- sort(deg, decreasing = T)
deg$ID1 <- row.names(deg)
usr_names <- merge(usr_names, deg, by = "ID1")
usr_names$deg <- as.numeric(usr_names$deg)
most_active_usr <- usr_names[which.max(usr_names$deg),]
most_active_usr <- most_active_usr$X
usr_net_deg       <- sna::degree(usr_net_matrix, cmode="freeman") # Freeman degree centrality without scaling i.e. raw count
usr_net_degscaled  <- sna::degree(usr_net_matrix, cmode="freeman", rescale=TRUE) # Freeman degree centrality with scaling 
usr_net_clus       <- sna::gtrans(usr_net_matrix) #transitivity/clustering
usr_net_geo        <- sna::geodist(usr_net_matrix, inf.replace = NA,
                                          count.paths = T) #geodesic distance/path length
#the path length between two unconnected nodes is set to infinite, so it was 
#replaced with NA to calculate a meaningful average.
usr_net_comp       <- sna::component.dist(usr_net_matrix, 
                                                 connected = "strong") #components

usr_net_stats <- c(nusers, most_active_usr, network.density(usr_net),mean(usr_net_deg),
                max(usr_net_deg), mean(usr_net_clus), mean(usr_net_geo$gdist, na.rm = T), 
                usr_net_comp$csize[1],usr_net_comp$csize[1]/nusers)
usr_net_stats <- as.data.frame(usr_net_stats)
usr_net_stats <- as.data.frame(t(usr_net_stats))
usr_net_stats <- (`colnames<-`(usr_net_stats, c("number of users", "most connected user",
                            "network density", "average centrality", 
                           "maximum centrality", "average clustering", 
                           "average geodesic distance", "size of the largest component",
                           "proportion of the largest component")))
usr_net_stats <- t(usr_net_stats)
usr_net_stats <- as.data.frame(usr_net_stats)
usr_net_stats <- round(usr_net_stats, digits = 3)
user_network_stats <- gridExtra::tableGrob(usr_net_stats, cols = "user network")
ggsave(file="user_network_statistics.png", user_network_stats)   


#----ERGM----
#to be added in the future



