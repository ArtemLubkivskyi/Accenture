# Accenture Bootcamp

My tasks and solutions from the Accenture bootcamp. Each day has its own folder.

| Day | Topic |
|-----|-------|
| [Day 1](./Day%201) | Data foundations |
| [Day 2](./Day%202) | Supervised learning |
| [Day 3](./Day%203) | Ensembles |
| [Day 4](./Day%204) | Clustering and PCA |
| [Day 5](./Day%205) | Text preprocessing |
| [Day 6](./Day%206) | Neural networks from scratch |
| [Day 7](./Day%207) | RNN, LSTM and Transformers |

## Day 1

Worked with the red wine quality dataset: basic exploration, Min-Max scaling, correlations, outliers, a few plots, a k-fold split and some new features.

Main thing I noticed: alcohol has the strongest link to quality, and wines with more alcohol tend to get better scores.

Notebook: [Day1 - Data foundations practical tasks](./Day%201/Day1%20-%20Data%20foundations%20practical%20tasks.ipynb)

## Day 2

Two parts. First regression on the advertising dataset: wrote my own MAE, MSE, RMSE, MAPE and R2 functions, trained linear regression, did 10-fold cross validation and tried Lasso, Ridge and Elastic Net. Then classification on the diabetes dataset: wrote accuracy, precision, recall and F1 myself and compared logistic regression with a decision tree, with ROC curves and AUC.

Main things I noticed: TV budget is what really drives sales and newspaper barely matters, the model got R2 around 0.85. For diabetes both models were close (accuracy about 0.74), but the tree caught more sick people while logistic regression had a better AUC. Data is not balanced so accuracy alone can be misleading.

Notebook: [Day 2 - Supervised learning practical tasks](./Day%202/Day%202%20-%20Supervised%20learning%20practical%20tasks.ipynb)

Also did both optional tasks: a [decision tree regressor](./Day%202/(Optional)%20Day%202%20-%20DecisionTreeRegressor.ipynb) on advertising (beat linear regression, R2 0.94 vs 0.85) and a [regressor used as a classifier](./Day%202/(Optional)%20Day%202%20-%20DecisionTreeRegressor%20classifier.ipynb) on diabetes.

## Day 3

Tree ensembles on the breast cancer dataset: trained a decision tree, random forest and gradient boosting on the same split, tuned the random forest with grid search and 5-fold CV, then compared everything with ROC-AUC, F1, ROC curves, a confusion matrix and feature importance.

Main things I noticed: all ensembles got ROC-AUC around 0.995 and the tuned random forest was best (0.996), while a single tree was clearly lower (0.976). The tree had the best F1, but the test set is small so I think that was luck. Tumour size and shape features matter the most, and the tuned forest missed only 2 of 53 malignant cases.

Notebook: [Day 3 - Ensembles practical task](./Day%203/Day%203%20-%20Ensembles%20practical%20task.ipynb)

## Day 4

Two parts. First clustering on the mall customers dataset: scaled income and spending score, picked the number of clusters with the elbow method and a dendrogram, then compared KMeans with hierarchical clustering. Also tried KMeans vs DBSCAN on half moons. Then PCA on the penguins dataset: cleaned missing and impossible values, reduced 4 features to 2 components, looked at loadings and used logistic regression to guess the sex of penguins where it was missing.

Main things I noticed: customers split nicely into 5 groups and both methods agreed. KMeans cuts the moons in half, DBSCAN finds them correctly because it follows density. For penguins 2 components already keep 88% of the variance, PC1 is basically body size. Predicting sex got about 80% accuracy, not great because the species are mixed together.

Notebook: [Day 4 - Clustering and PCA practical tasks](./Day%204/Day4_practice.ipynb)

## Day 5

Text preprocessing with NLTK on the author identification dataset (sentences by Lovecraft, Poe and Shelley). Wrote functions for sentence and word tokenization, stopword and punctuation removal, stemming, lemmatization, a wordcloud and the most common verbs and nouns using POS tags. Then built simple text features (token count, characters, capitals, average word length) and compared XGBoost on them with Naive Bayes and logistic regression on bag of words.

Main things I noticed: stemming is fast but gives cut words like "fumbl", lemmas stay real words. The most common verbs are just forms of "be" and "have". Simple text features alone only got about 0.48 accuracy, while bag of words was much better: Naive Bayes 0.84 and logistic regression 0.81 on the test set. Logistic regression overfits (0.98 on train), and trying TF-IDF with different C values only got it to 0.82, so Naive Bayes stayed the best.

Notebook: [Day 5 - Text preprocessing pipeline](./Day%205/Text_Preprocessing_Pipeline.ipynb)

## Day 6

A small neural network written in NumPy (one tanh hidden layer, sigmoid output) on a 2D flower-shaped dataset. Ran the notebook, tried hidden layer sizes from 1 to 100 with 100 points kept as a test set, and trained the 50 unit network longer to check for overfitting.

Main things I noticed: 1 or 2 units only draw a straight line (about 65% accuracy), from 3 units it jumps to about 90% and more units don't really help. Training 50 units for 20000 iterations instead of 5000 raised train accuracy from 92.3% to 95.7% while test stayed at 88%, so a big layer starts to overfit. 3 to 5 units look like the best choice.

Notebook: [Day 6 - NN from scratch task 1](./Day%206/NN_from_scratch_task_nr_1_excercise.ipynb)

### Part 2

A deeper NumPy network on MNIST (784 → 30 → 20 → 15 → 10, ReLU hidden layers, softmax output), trained with full batch gradient descent. Filled in forward and backward propagation, the parameter updates and the training loop, then evaluation with a confusion matrix, plots of the misclassified digits and saliency maps showing which pixels push the loss the most.

Notebook: [Day 6 - NN from scratch on MNIST task 2](./Day%206/NN_From_Scratch_on_MNIST_task_nr_2_excercise.ipynb)

## Day 7

Three sequence model labs. A SimpleRNN predicting Google's next opening price, and an LSTM predicting monthly airline passengers. For both I changed only the lookback window, picked it on validation, and ran the test once. Then Hugging Face pipelines: tokens vs words, fill-mask, a sentiment stress test and bounded text generation (sampling vs greedy). I also did the investigation part with cased BERT.

Main things I noticed: the simple baselines won both time series labs. Repeating yesterday's price beat the RNN (test MAE 5.9 vs 10.6 USD), and both "last month" and "same month last year" beat the LSTM, which can't extrapolate past the training range. 12 months of history was the best LSTM window, while 6 months misses the yearly pattern. The sentiment model labels "The meeting starts at two o'clock." as POSITIVE with 0.98 confidence, because it has no neutral class. Changing "bank" to "kitchen" moves the fill-mask guess from "rates" to "once". Cased BERT keeps "Apple" and "New York" whole, but still doesn't guess the company name.

Notebooks: [RNN](./Day%207/RNN_assignment.ipynb) · [LSTM](./Day%207/LSTM_assignment.ipynb) · [Transformers](./Day%207/Transformers_assignment.ipynb)
