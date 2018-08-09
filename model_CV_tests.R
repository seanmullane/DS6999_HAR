
# This script is for training models on accelerometer sensor data for HAR

setwd("C:/Users/spm9r/eclipse-workspace-spm9r/DS6999_HAR/")

# --------------------------------------------------------------------------------------------------------
# Load libraries
# --------------------------------------------------------------------------------------------------------

library(tidyverse)

# --------------------------------------------------------------------------------------------------------
# Load model CV result data
# --------------------------------------------------------------------------------------------------------

load("glmnet/glmnet_model_results.RData")
reslist_glmnet <- modelResultsList

load("knn/knn_model_results.RData")
reslist_knn <- modelResultsList

load("log_reg/LogitBoost_model_results.RData")
reslist_logitboost <- modelResultsList

load("svm/svmLinear_model_results.RData")
reslist_svmlinear <- modelResultsList

# --------------------------------------------------------------------------------------------------------
# Data processing
# --------------------------------------------------------------------------------------------------------

rindv <- c(5, 10, 25, 50)
cindv <- c(1, 2, 3, 5, 10)

m <- matrix(data = NA, nrow = 4, ncol = 5)

# Create matrices for results

m.acc <- m
m.sd <- m
l.samples <- list(20)
for (i in 1:length(reslist_glmnet)) {
  #print(reslist_glmnet[[i]]) 
  rind <- which(rindv == reslist_glmnet[[i]]$data_frequency)
  cind <- which(cindv == reslist_glmnet[[i]]$data_window)
  print(rind, cind)
  samples <- reslist_glmnet[[i]]$model_resample$Accuracy
  l.samples[[i]] <- samples
  m.acc[rind, cind] <- round(mean(samples), 4)
  m.sd[rind, cind] <- round(sd(samples), 4)
}
colnames(m.acc) <- paste0(cindv, "s")
colnames(m.sd) <- paste0(cindv, "s")
rownames(m.acc) <- paste0(rindv, "Hz")
rownames(m.sd) <- paste0(rindv, "Hz")

print(m.acc)
print(m.sd)

# Best window & freq
best_inds <- arrayInd(which.max(m.acc), dim(m.acc), dimnames(m.acc), T); best_inds
max(m.acc)

# One-sided hypothesis test (Welch Two Sample t-test)
# H_0: difference in mean accuracy between samples is 0
# H_A: mean accuracy in sample 1 is greater than mean accuracy in sample 2
tt <- t.test(l.samples[[which.max(m.acc)]], l.samples[[1]], alternative = "greater", mu = 0); tt

