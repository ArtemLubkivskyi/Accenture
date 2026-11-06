# Accenture Bootcamp

My tasks and solutions from the Accenture bootcamp. Each day has its own folder.

| Day | Topic |
|-----|-------|
| [Day 1](./Day%201) | Data foundations |
| [Day 2](./Day%202) | Supervised learning |
| Day 3 | |
| [Day 4](./Day%204) | Clustering and PCA |

## Day 1

Worked with the red wine quality dataset: basic exploration, Min-Max scaling, correlations, outliers, a few plots, a k-fold split and some new features.

Main thing I noticed: alcohol has the strongest link to quality, and wines with more alcohol tend to get better scores.

Notebook: [Day1 - Data foundations practical tasks](./Day%201/Day1%20-%20Data%20foundations%20practical%20tasks.ipynb)

## Day 2

Two parts. First regression on the advertising dataset: wrote my own MAE, MSE, RMSE, MAPE and R2 functions, trained linear regression, did 10-fold cross validation and tried Lasso, Ridge and Elastic Net. Then classification on the diabetes dataset: wrote accuracy, precision, recall and F1 myself and compared logistic regression with a decision tree, with ROC curves and AUC.

Main things I noticed: TV budget is what really drives sales and newspaper barely matters, the model got R2 around 0.85. For diabetes both models were close (accuracy about 0.74), but the tree caught more sick people while logistic regression had a better AUC. Data is not balanced so accuracy alone can be misleading.

Notebook: [Day 2 - Supervised learning practical tasks](./Day%202/Day%202%20-%20Supervised%20learning%20practical%20tasks.ipynb)

Also did both optional tasks: a [decision tree regressor](./Day%202/(Optional)%20Day%202%20-%20DecisionTreeRegressor.ipynb) on advertising (beat linear regression, R2 0.94 vs 0.85) and a [regressor used as a classifier](./Day%202/(Optional)%20Day%202%20-%20DecisionTreeRegressor%20classifier.ipynb) on diabetes.

## Day 4

Two parts. First clustering on the mall customers dataset: scaled income and spending score, picked the number of clusters with the elbow method and a dendrogram, then compared KMeans with hierarchical clustering. Also tried KMeans vs DBSCAN on half moons. Then PCA on the penguins dataset: cleaned missing and impossible values, reduced 4 features to 2 components, looked at loadings and used logistic regression to guess the sex of penguins where it was missing.

Main things I noticed: customers split nicely into 5 groups and both methods agreed. KMeans cuts the moons in half, DBSCAN finds them correctly because it follows density. For penguins 2 components already keep 88% of the variance, PC1 is basically body size. Predicting sex got about 80% accuracy, not great because the species are mixed together.

Notebook: [Day 4 - Clustering and PCA practical tasks](./Day%204/Day4_practice.ipynb)
