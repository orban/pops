library('pcalg')
library('rjson')

# getting the data
dfCI <- read.csv("./app_data/df_CI_R.csv")

# fitting the causal analysis algorithm
suffStat <- list(C = cor(dfCI), n = nrow(dfCI))
pc.fit <- pc(suffStat, indepTest = gaussCItest, p = ncol(dfCI), alpha = 0.01)

suffStat <- list(C = cor(dfCI), n = nrow(dfCI))
pc.fit <- pc(suffStat, indepTest = gaussCItest, p = ncol(dfCI), alpha = 0.01)
## plot(pc.fit, main='')

# ---------------------------------
# making a json file of the graph
# ---------------------------------
featureNames <- toupper(names(dfCI))

# making a string for vertices
verticesStr<- '"vertices": ['
for (i in seq(length(featureNames))) {
    name <- featureNames[i]
    if (0 == length(pc.fit@graph@edgeL[[i]]$edges)) {
        friends <- ''
    } else {
        friends <- toString(paste(pc.fit@graph@edgeL[[i]]$edges-1,collapse=","))
    }
    
    verticesStr <- paste(verticesStr, '{"name":"',name, '"',
                         ', "node": ', i - 1,
                         ', "friends": "', friends, '"},',                         
                         sep='')
}
verticesStr <- substr(verticesStr, 1, nchar(verticesStr)-1)
verticesStr <- paste(verticesStr,']', sep='')

#making a string for edges
counter <- 0
edgesStr <- '"edges": ['
for (node in pc.fit@graph@nodes) {
    # move on the next node if points to nothing
    if (0 == length(pc.fit@graph@edgeL[[node]]$edges)) {
        next
    }
    nodeNum = as.integer(node) - 1
    for (target in pc.fit@graph@edgeL[[node]]$edges) {
        counter <- counter + 1
        targetNum = target - 1

        # causal effect
        tryCatch(effs <- ida(as.integer(node), as.integer(target),
                             suffStat$C, pc.fit@graph, method='local'),
                 error = function(e) {
                     effs <<- 0.0
                 }
                 )
        effect <- mean(effs)

        # creating json
        edgesStr <- paste(edgesStr, '{"source":', as.integer(nodeNum),
                          ', "target":', as.integer(targetNum),
                          ', "effect": ', effect,
                          ', "strength": ', abs(effect),
                          ', "sign": ', sign(effect),                          
                          '},', sep='')
    }
}
edgesStr <- substr(edgesStr, 1, nchar(edgesStr)-1)
edgesStr <- paste(edgesStr,']', sep='')

tmptJSON <- paste('{', verticesStr, ',\n', edgesStr, '\n }', sep='')
## f <- file('./static/data/hist_cr.json')
## write(tmptJSON, f)
## close(f)
