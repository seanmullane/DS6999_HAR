
# This script is for training models on accelerometer sensor data for HAR

#setwd("C:/Users/spm9r/eclipse-workspace-spm9r/DS6999_HAR/")
setwd("~/DSI/classes/DS6999/DS6999_HAR/")

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

l.allmodels <- list(reslist_glmnet, reslist_knn, reslist_logitboost, reslist_svmlinear)
names(l.allmodels) <- c("GLMnet", "KNN", "LogitBoost", "SVMLinear")

# --------------------------------------------------------------------------------------------------------
# Data processing
# --------------------------------------------------------------------------------------------------------


l.alloutputs <- list()
for (j in 1:4) {
  
  reslist <- l.allmodels[[j]]
  
  # Create data frame to pre-sort results
  l_r_a <- list(20)
  for (i in 1:20) { 
    l_r_a[[i]] <- as.list(reslist[[i]]$model_resample$Accuracy)
  }
  d.res <- data.frame(freq = as.integer(unlist(lapply(reslist, "[[", "data_frequency"))),
                      window = as.integer(unlist(lapply(reslist, "[[", "data_window"))))
  m.acc.sample <- matrix(unlist(l_r_a), nrow = 20, ncol = 10, byrow = T)
  d.accsample <- as.data.frame(m.acc.sample)
  d.res <- cbind(d.res, m.acc.sample)
  d.res <- d.res %>% arrange(window, freq)
  rm(l_r_a, m.acc.sample)
  
  d.res2 <- d.res %>%
    gather(samp_elem, model_acc, -freq, -window) %>%
    group_by(freq, window) %>%
    summarise(mean_acc = mean(model_acc),
              sd_acc = sd(model_acc)) %>%
    ungroup %>%
    arrange(window, freq)
  
  # Create matrix to contain results
  rindv <- c(5, 10, 25, 50)
  cindv <- c(1, 2, 3, 5, 10)
  
  m <- matrix(data = NA, nrow = 4, ncol = 5)
  colnames(m) <- paste0(cindv, "s")
  rownames(m) <- paste0(rindv, "Hz")
  
  # Populate matrices for results
  m.acc <- m
  m.sd <- m
  for (i in 1:20) {
    m.acc[i] <- mean(unlist(d.res[i,3:12]))
    m.sd[i] <- sd(unlist(d.res[i,3:12]))
  }
  
  print(m.acc)
  print(m.sd)
  
  # Best window & freq, get list index of best mean and all other list indices
  best_m_inds <- arrayInd(which.max(m.acc), dim(m.acc), dimnames(m.acc), T); best_m_inds
  best_ind <- which.max(d.res2$mean_acc)
  other_inds <- which(best_ind != 1:20)
  
  # Get p-values from hypothesis tests
  m.pval <- m
  for (i in other_inds) {
    # One-sided hypothesis test (Welch Two Sample t-test)
    # H_0: difference in mean accuracy between samples is 0
    # H_A: mean accuracy in sample 1 is greater than mean accuracy in sample 2
    tt <- t.test(unlist(d.res[best_ind,3:12]), unlist(d.res[i,3:12]), alternative = "greater", mu = 0)
    m.pval[[i]] <- round(tt$p.value, digits = 4)
  }
  
  print(m.pval)
  
  l.alloutputs[[j]] <- list(m.acc, m.sd, m.pval)
}

for (j in 1:4) {
  print(names(l.allmodels)[[j]])
  print(l.alloutputs[[j]][[3]])
}

# Need to apply bonferroni correction for multiple comparisons