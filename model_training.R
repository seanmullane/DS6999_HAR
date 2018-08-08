
# This script is for training models on accelerometer sensor data for HAR

setwd("C:/Users/spm9r/eclipse-workspace-spm9r/DS6999_HAR/data/FeatureData/")

# --------------------------------------------------------------------------------------------------------
# Load libraries
# --------------------------------------------------------------------------------------------------------

library(tidyverse)
library(stringr)
library(caret)

# Enable parallel processing
library(doParallel)
cl <- makePSOCKcluster(6)
doParallel::registerDoParallel(cl)


files <- Sys.glob("*.csv")

modelResultsList <- list()

for (j in 1:length(files)) {
  fname = files[[j]]
  # Add training code inside this loop later
  
  # This list collects all rlevant information on a single model for a single data set
  # Further information will be added to this list as it is generated
  modelinfo <- list(
    str_match(fname, '\\d+')[1],
    str_match(fname, '(\\d+)s')[2]
  )

  #print(modelinfo[[1]])
  #print(modelinfo[[2]])
  
  message(paste0("Reading in data file: ", fname))
  
  # Read in all columns as numeric
  d.file <- read_tsv(fname, col_types = cols(.default = "d"))
  
  message(paste0("Filtering NAs for ", fname))
  
  # View NAs
  nas <- sapply(d.file, function(x) {1.0*sum(is.na(x))/length(x)})
  #d.nas <- data.frame(colname = colnames(d.file), nas = nas)
  
  # Keep only columns without NAs
  d.frame <- d.file[,which(nas < 0.05)]
  d.frame <- d.frame %>% select(-experimentID, -index)
  
  # Filter out rows with activityID == 0
  d.frame <- d.frame %>% filter(activityID != 0)
  d.frame <- d.frame %>% mutate_at(.vars = c("activityID"), .funs = as.factor)
  
  # Separate response variable
  trainY <- d.frame$activityID

  message(paste0("Removing Infs for ", fname))
    
  # Replace any Inf values with NA
  mat.train <- as.matrix(d.frame %>% select(-X1, -userID, -activityID))
  mat.train[is.infinite(mat.train)] <- NA
  
  tc.lm <- trainControl(
    method = "boot",
    number= 10,
    repeats = 1)
  
  #mname <- "LogitBoost"
  #mname <- "svmLinear"
  #mname <- "J48"
  mname <- "knn"
  #mname <- "rf"
  
  message(paste0("Training ", mname ," model for: ", fname))
  
  # Models that work for this data:
  # LogitBoost  # elapsed: 298s
  # svmLinear   # elapsed: 145s
  # J48         # elapsed: 818s
  # knn         # elapsed: 923s
  # rf          # elapsed: 6213s # This may need rf.cores to run faster
    
  t <- system.time(m.linear <- train(x = mat.train, 
                    y = trainY, 
                    method = mname, 
                    trControl = tc.lm, 
                    preProcess =c("center", "scale", "zv", "nzv", "medianImpute")))
  
  modelinfo[[3]] <- m.linear$results
  modelinfo[[4]] <- m.linear$method
  modelinfo[[5]] <- m.linear$bestTune
  modelinfo[[6]] <- m.linear$resample
  modelinfo[[7]] <- t
  
  names(modelinfo) <- c("data_frequency","data_window","model_best_results","model_method","model_bestTune","model_resample", "training_time")
  
  message(paste0(mname, " model trained in ", t, " time"))
  print(m.linear)
  
  modelResultsList[[j]] <- modelinfo
  gc()
}

save(list = "modelResultsList", file = paste0(mname, "_model_results.RData"))

m4 <- modelResultsList[[1]]


ll <- list()
for (i in 1:20) {
  ll[[i]] <- modelResultsList[[i]]$model_best_results[[2]]
}
which.max(unlist(ll))
max(unlist(ll))








## Split test/train on user IDs for best simulation of reality
#trainUserIDs <- sample(1:30, size = 20, replace = F)
#
#d.train <- d.frame %>% filter(userID %in% trainUserIDs)
#d.test <- anti_join(
#  d.frame,
#  d.train,
#  by = "X1")
#
#trainY <- d.train$activityID
#testY <- d.test$activityID
#
#d.train <- d.train %>% select(-X1, -userID, -activityID)
#d.test <- d.test %>% select(-X1, -userID, -activityID)
#
#mat.train <- as.matrix(d.train)
#mat.train[is.infinite(mat.train)] <- NA
#
#mat.test <- as.matrix(d.test)
#mat.test[is.infinite(mat.test)] <- NA
#            



#preProc <- caret::preProcess(x = mat.train,
#                                method = c("center", "scale", "zv", "nzv", "medianImpute")
#)

#mat.trainSet <- predict(preProc, newdata = mat.train)
#d.trainSet$activityID <- d.train$activityID
#mat.testSet <- predict(preProc, newdata = mat.test)

# Use default train control for now
tc.lm <- trainControl(
  method = "boot",
  number= 10,
  repeats = 1)

m.linear <- train(x = mat.train, 
                  y = trainY, 
                  method = "LogitBoost", 
                  trControl = tc.lm, 
                  preProcess =c("center", "scale", "zv", "nzv", "medianImpute"))

modelinfo[[3]] <- m.linear$results
modelinfo[[4]] <- m.linear$method
modelinfo[[5]] <- m.linear$bestTune
modelinfo[[6]] <- m.linear$resample

names(modelinfo) <- c("data_frequency","data_window","model_best_results","model_method","model_bestTune","model_resample")



#m.test <- glm(formula = y ~ ., cbind(as.data.frame(mat.trainSet), data.frame(y = trainY)), family = "binomial")


# Loop through testing several models with cross-validation and save results to list


for (j in 1:length(files)) {
  fname = files[[j]]
  print(ncol(read_tsv(fname, col_types = cols(.default = "d"))))
}