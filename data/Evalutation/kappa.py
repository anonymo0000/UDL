import numpy as np
import statsmodels.stats.inter_rater as irr




import pickle

with open(r'RQ2_test_acc_label.data','rb') as f:
    data_s = pickle.load(f)

ratings = np.array(data_s)


ratings_transposed = np.transpose(ratings)

def ratings_to_counts(ratings, num_categories):
    num_items, num_raters = ratings.shape
    counts = np.zeros((num_items, num_categories), dtype=int)
    
    for i in range(num_items):
        for rating in ratings[i]:
            counts[i][rating - 1] += 1
    
    return counts


num_categories = 5 
counts_matrix = ratings_to_counts(ratings_transposed, num_categories)

# 计算 Fleiss' Kappa
kappa = irr.fleiss_kappa(counts_matrix, method='fleiss')
print(f"Fleiss' Kappa: {kappa:.4f}")


    