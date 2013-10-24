library('pcalg');
library('rjson');

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# data for causal inference analysis
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
dfCI <- read.csv('./app_data/df_CI_R.csv');

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# fitting the causal analysis algorithm
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
suffStat <- list(C = cor(dfCI), n = nrow(dfCI));
pc.fit <- pc(suffStat, indepTest = gaussCItest, p = ncol(dfCI), alpha = 0.01)
## plot(pc.fit, main='')

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# fitting the causal analysis algorithm
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

## > names(df_CI)
##  [1] "starters_3p_per"   "reserves_fg_per"   "starters_ast"     
##  [4] "starters_fg"       "starting_g_fg_per" "starting_f_fg_per"
##  [7] "starters_trb_per"  "starters_drb"      "starters_pts"     
## [10] "starters_fg_per"   "result"

## pc.fit@graph@nodes
##  [1] "1"  "2"  "3"  "4"  "5"  "6"  "7"  "8"  "9"  "10" "11"

## > names(pc.fit@graph@edgeL)
##  [1] "1"  "2"  "3"  "4"  "5"  "6"  "7"  "8"  "9"  "10" "11"

## > pc.fit@graph@edgeL$'2'
## $edges
## [1]  3  8 11

## library('rjson');
## x <- list( alpha = 1:5, beta = "Bravo",
##                gamma = list(a=1:3, b=NULL),
##                delta = c(TRUE, FALSE) );
## json <- toJSON(x);
## f <- file('./tmpt/output.txt');
## write(json, f);
## close(f);



# --------------------------------
# making a json file of the graph
# --------------------------------
featureNames <- toupper(names(df_CI));
# making a string for vertices
verticesStr<- '"vertices": [';
for (name in featureNames) {
    verticesStr <- paste(verticesStr, '{"name":"',name, '"},', sep='');
};
verticesStr <- substr(verticesStr, 1, nchar(verticesStr)-1)
verticesStr <- paste(verticesStr,']', sep='');

#making a string for edges
edgesStr <- '"edges": [';
for (node in pc.fit@graph@nodes) {
    # move on the next node if
    # it points to nothing
    if (0 == length(pc.fit@graph@edgeL[[node]]$edges)) {
        next;
    }
    nodeNum = as.integer(node) - 1;
    for (target in pc.fit@graph@edgeL[[node]]$edges) {
        targetNum = target - 1;
        edgesStr <- paste(edgesStr, '{"source":', as.integer(nodeNum),
                          ', "target":', as.integer(targetNum), '},', sep='');
    }
}
edgesStr <- substr(edgesStr, 1, nchar(edgesStr)-1)
edgesStr <- paste(edgesStr,']', sep='');

json <- paste('{', verticesStr, ',\n', edgesStr, '\n }', sep='');
f <- file('./templates/static/data/hist_cr.json');
write(json, f);
close(f);
