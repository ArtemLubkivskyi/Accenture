# Accenture Bootcamp

My tasks and solutions from the Accenture bootcamp. Each day has its own folder.

## About me

I'm Artem Lubkivskyi, a student at SSE Riga (BSc Economics and Business). Before that I was a Research Student at the University of Tokyo (2022–2024), working on real-time object detection for safety monitoring. I learned machine learning before the bootcamp, and what I enjoy most is taking a model out of the theory and trying it on real data to see what actually works. I joined the Accenture bootcamp to go through the whole path, from cleaning data and classic models to neural networks, LLMs and vector search. This repo is where I keep my work from each day, together with short notes on what I noticed.

Languages: English, Ukrainian and Russian (fluent), Latvian (basic).

GitHub: [ArtemLubkivskyi](https://github.com/ArtemLubkivskyi)

## Highlights

- [Day 11–12](#day-11): a RAG pipeline that runs fully on a CPU laptop (16 of 19 test answers passed), then my own evaluation of it against a cloud model with DeepEval.
- [Day 12](#day-12): a hidden instruction in a document worked on both the local and the cloud model (both added "Verified by HR-Bot 7"), and the cloud model answered "5 days remote" from a poisoned file.
- [Day 7](#day-7): simple baselines beat the neural nets, repeating yesterday's price beat the RNN (test MAE 5.9 vs 10.6 USD).
- [Day 14](#day-14): a tool that returned "1000 EUR = 1000.00 JPY" for a missing rate was repeated by the agent without question, so tools should return errors, not fake values.

| Day | Topic |
|-----|-------|
| [Day 1](./Day%2001) | Data foundations |
| [Day 2](./Day%2002) | Supervised learning |
| [Day 3](./Day%2003) | Ensembles |
| [Day 4](./Day%2004) | Clustering and PCA |
| [Day 5](./Day%2005) | Text preprocessing |
| [Day 6](./Day%2006) | Neural networks from scratch |
| [Day 7](./Day%2007) | RNN, LSTM and Transformers |
| [Day 8](./Day%2008) | LLM foundations and prompting |
| [Day 9](./Day%2009) | Embeddings and vector search |
| [Day 10](./Day%2010) | Advanced RAG patterns |
| [Day 11](./Day%2011) | Local RAG with Ollama |
| [Day 12](./Day%2012) | RAG evaluation and security |
| [Day 13](./Day%2013) | Agentic AI and ReAct agents |
| [Day 14](./Day%2014) | Agent frameworks |

## Day 1

Worked with the red wine quality dataset: basic exploration, Min-Max scaling, correlations, outliers, a few plots, a k-fold split and some new features.

Main thing I noticed: alcohol has the strongest link to quality, and wines with more alcohol tend to get better scores.

Notebook: [Day1 - Data foundations practical tasks](./Day%2001/Day1%20-%20Data%20foundations%20practical%20tasks.ipynb)

## Day 2

Two parts. First regression on the advertising dataset: wrote my own MAE, MSE, RMSE, MAPE and R2 functions, trained linear regression, did 10-fold cross validation and tried Lasso, Ridge and Elastic Net. Then classification on the diabetes dataset: wrote accuracy, precision, recall and F1 myself and compared logistic regression with a decision tree, with ROC curves and AUC.

Main things I noticed: TV budget is what really drives sales and newspaper barely matters, the model got R2 around 0.85. For diabetes both models were close (accuracy about 0.74), but the tree caught more sick people while logistic regression had a better AUC. Data is not balanced so accuracy alone can be misleading.

Notebook: [Day 2 - Supervised learning practical tasks](./Day%2002/Day%202%20-%20Supervised%20learning%20practical%20tasks.ipynb)

Also did both optional tasks: a [decision tree regressor](./Day%2002/(Optional)%20Day%202%20-%20DecisionTreeRegressor.ipynb) on advertising (beat linear regression, R2 0.94 vs 0.85) and a [regressor used as a classifier](./Day%2002/(Optional)%20Day%202%20-%20DecisionTreeRegressor%20classifier.ipynb) on diabetes.

## Day 3

Tree ensembles on the breast cancer dataset: trained a decision tree, random forest and gradient boosting on the same split, tuned the random forest with grid search and 5-fold CV, then compared everything with ROC-AUC, F1, ROC curves, a confusion matrix and feature importance.

Main things I noticed: all ensembles got ROC-AUC around 0.995 and the tuned random forest was best (0.996), while a single tree was clearly lower (0.976). The tree had the best F1, but the test set is small so I think that was luck. Tumour size and shape features matter the most, and the tuned forest missed only 2 of 53 malignant cases.

Notebook: [Day 3 - Ensembles practical task](./Day%2003/Day%203%20-%20Ensembles%20practical%20task.ipynb)

## Day 4

Two parts. First clustering on the mall customers dataset: scaled income and spending score, picked the number of clusters with the elbow method and a dendrogram, then compared KMeans with hierarchical clustering. Also tried KMeans vs DBSCAN on half moons. Then PCA on the penguins dataset: cleaned missing and impossible values, reduced 4 features to 2 components, looked at loadings and used logistic regression to guess the sex of penguins where it was missing.

Main things I noticed: customers split nicely into 5 groups and both methods agreed. KMeans cuts the moons in half, DBSCAN finds them correctly because it follows density. For penguins 2 components already keep 88% of the variance, PC1 is basically body size. Predicting sex got about 80% accuracy, not great because the species are mixed together.

Notebook: [Day 4 - Clustering and PCA practical tasks](./Day%2004/Day4_practice.ipynb)

## Day 5

Text preprocessing with NLTK on the author identification dataset (sentences by Lovecraft, Poe and Shelley). Wrote functions for sentence and word tokenization, stopword and punctuation removal, stemming, lemmatization, a wordcloud and the most common verbs and nouns using POS tags. Then built simple text features (token count, characters, capitals, average word length) and compared XGBoost on them with Naive Bayes and logistic regression on bag of words.

Main things I noticed: stemming is fast but gives cut words like "fumbl", lemmas stay real words. The most common verbs are just forms of "be" and "have". Simple text features alone only got about 0.48 accuracy, while bag of words was much better: Naive Bayes 0.84 and logistic regression 0.81 on the test set. Logistic regression overfits (0.98 on train), and trying TF-IDF with different C values only got it to 0.82, so Naive Bayes stayed the best.

Notebook: [Day 5 - Text preprocessing pipeline](./Day%2005/Text_Preprocessing_Pipeline.ipynb)

## Day 6

A small neural network written in NumPy (one tanh hidden layer, sigmoid output) on a 2D flower-shaped dataset. Ran the notebook, tried hidden layer sizes from 1 to 100 with 100 points kept as a test set, and trained the 50 unit network longer to check for overfitting.

Main things I noticed: 1 or 2 units only draw a straight line (about 65% accuracy), from 3 units it jumps to about 90% and more units don't really help. Training 50 units for 20000 iterations instead of 5000 raised train accuracy from 92.3% to 95.7% while test stayed at 88%, so a big layer starts to overfit. 3 to 5 units look like the best choice.

Notebook: [Day 6 - NN from scratch task 1](./Day%2006/NN_from_scratch_task_nr_1_excercise.ipynb)

### Part 2

A deeper NumPy network on MNIST (784 → 30 → 20 → 15 → 10, ReLU hidden layers, softmax output), trained with full batch gradient descent. Filled in forward and backward propagation, the parameter updates and the training loop, then evaluation with a confusion matrix, plots of the misclassified digits and saliency maps showing which pixels push the loss the most.

Main things I noticed: after 3000 iterations the network gets 79.1% on train and 79.4% on test, so it does not overfit, it just does not learn enough, and the cost went down to about 0.016 and then jumped back to 0.065 at the end (once even to 0.21), so a learning rate of 0.9 looks too high. The most common test mistakes are 9 read as 7 (299 times), 3 as 8 (249) and 7 as 9 (192). The saliency maps were hard to read, in most of the 80 mistakes the gradient is only a faint haze around the stroke.

Notebook: [Day 6 - NN from scratch on MNIST task 2](./Day%2006/NN_From_Scratch_on_MNIST_task_nr_2_excercise.ipynb)

## Day 7

Three sequence model labs. A SimpleRNN predicting Google's next opening price, and an LSTM predicting monthly airline passengers. For both I changed only the lookback window, picked it on validation, and ran the test once. Then Hugging Face pipelines: tokens vs words, fill-mask, a sentiment stress test and bounded text generation (sampling vs greedy). I also did the investigation part with cased BERT.

Main things I noticed: the simple baselines won both time series labs. Repeating yesterday's price beat the RNN (test MAE 5.9 vs 10.6 USD), and both "last month" and "same month last year" beat the LSTM, which can't extrapolate past the training range. 12 months of history was the best LSTM window, while 6 months misses the yearly pattern. The sentiment model labels "The meeting starts at two o'clock." as POSITIVE with 0.98 confidence, because it has no neutral class. Changing "bank" to "kitchen" moves the fill-mask guess from "rates" to "once". Cased BERT keeps "Apple" and "New York" whole, but still doesn't guess the company name.

Notebooks: [RNN](./Day%2007/RNN_assignment.ipynb) · [LSTM](./Day%2007/LSTM_assignment.ipynb) · [Transformers](./Day%2007/Transformers_assignment.ipynb)

## Day 8

Calling the OpenAI API (`gpt-5.6-luna` and `gpt-5.4-mini`) and prompting. Compared the two models, then changed one setting at a time: temperature, max output tokens, top_p, frequency and presence penalty. After that system prompts, zero-shot vs few-shot, cutting input and output tokens, rewriting prompts for format, style and audience, generating and fixing code, summarizing, translating idioms to Ukrainian, a story without the letter "e", JSON extraction and prompts that copy an exact format (table, quiz, course outline).

Main things I noticed: at temperature 0 two of three stories were word for word the same, at 1.5 all were different. The max tokens limit just cuts the answer, even 200 tokens stopped mid-sentence, so length is better asked for in the prompt. Low top_p gave almost the same hobby lists, "cloud shadow spotting" showed up nearly every time. Shortening the prompt went from 94 to 27 input tokens with the same quality, and the answer went from 277 to 9 output tokens. The no "e" story kept failing until I let the model reason first (`reasoning_effort="medium"`), then 3 of 3 were clean. A JSON schema gave a proper date and integer, while the prompt-only version returned "June 12th" and "5 nights" as text. Answers change on every run, so the conclusions match the saved outputs.

Notebook: [Day 8 - LLM foundations practical tasks](./Day%2008/Day%208%20-%20LLM%20foundations%20practical%20tasks.ipynb)

## Day 9

Three parts about embeddings and vector search. First local embeddings with sentence-transformers (`paraphrase-MiniLM-L6-v2`): encoded ten sentences on different topics, compared them with `util.cos_sim`, wrote a function that ranks the sentences for any question, and my own cosine similarity in NumPy for one vector against a batch. Then a FAISS `IndexFlatL2` with 100 000 random vectors of length 768 and a search for the 5 nearest ones. Last, Pinecone: created a serverless index, made embeddings with the hosted `multilingual-e5-large` model, upserted my own sentences and searched them with a question.

Main things I noticed: each sentence becomes a vector of 384 numbers. Rain vs storm got 0.245 and rain vs dog -0.087, so the topic shows even when the score is not high. "Where can I get some good food in town?" found the restaurant first (0.418) and the pancakes second, and the NumPy version gives the same numbers as `util.cos_sim`. FAISS needs float32 and a 2D query, a flat index needs no training, and the distance it returns is the squared L2 (104.43 both ways). With random data all 5 neighbours are almost equally far (104 to 106), so there is nothing really "similar" to find. In Pinecone "How can I sleep better at night?" returned three sleep tips, but the e5 scores are all very close (0.84 to 0.85), so the ranking says more than the score itself.

Notebooks: [Embeddings](./Day%2009/Embedding_and_Vector_Search_practical_tasks.ipynb) · [FAISS](./Day%2009/FAISS_Creation_practical_tasks.ipynb) · [Pinecone](./Day%2009/Pinecone_vector_database_practical_tasks_.ipynb)

## Day 10

A small advanced RAG pipeline on eight short documents with built-in traps (an old and a new refund policy, X100 vs X200 warranties, the error code E-4711 and a confidential finance note). Wrote fixed-length chunking, a BM25 and a dense index, a metadata and access filter, reciprocal rank fusion for hybrid search, cross-encoder re-ranking, small-to-big parents, multi-query and HyDE search, a grounded prompt with citations, Recall@k and MRR, and timing for each stage.

Main things I noticed: BM25 finds the exact code E-4711 but fails on "money back for a yearly plan", where dense search finds the refund policy. Without the filter the confidential note (60 days) came first for the refund question, with it the 2024 policy (14 days) wins. Re-ranking moved the "24 months" sentence to the top for the X200 question, but it is the slowest stage by far (about 150 ms vs about 14 ms for hybrid search). On the 6 question golden set the filter gave the biggest gain (MRR 0.92 to 1.00), but one question already changes recall by 0.17, so this set is too small to prove much.

Notebook: [Day 10 - Advanced RAG patterns](./Day%2010/Advanced_RAG_Patterns.ipynb)

## Day 11

A document Q&A pipeline that runs fully on my laptop, for five PDFs of a made-up company (handbook, product guide, security policy, quarterly report, meeting notes). Everything goes through Ollama on the CPU: `nomic-embed-text` for embeddings, Chroma as the vector store, `qwen3.5:4b-q4_K_M` with thinking turned off for the answers. Text comes from `pypdf`, split per page into 512 character chunks with 50 overlap (330 chunks), top-5 retrieval. Before choosing the model I compared the 4b and 2b versions on 7 prompts, then ran 19 test questions and rated the answers.

Main things I noticed: the 2b model is about twice as fast (11.0 vs 4.8 tokens/s) but made real mistakes, so I kept the 4b one (rating 4.57 vs 3.71). 16 of 19 answers passed, including the three questions with no answer in the documents, where it did not make anything up. The failures: q06 answered Salesforce instead of HubSpot because the February decision was not in the top 5 (with top-10 it shows up at rank 7), q15 had both conflicting dates in the context but only gave one, and q08 had the right price but skipped the calculation. Speed is the main problem: about 52 s per answer on average and up to 139 s.

Code and notes: [local-rag](./Day%2011/local-rag) · [decision log](./Day%2011/local-rag/decision_log.md)

## Day 12

Evaluated my own Day 11 pipeline instead of the reference one. Ran the 19 questions with DeepEval metrics (faithfulness, answer relevancy, contextual relevancy, recall and precision) for the local model and for the cloud `gpt-5.6-luna`, compared them with a ± range, checked retrieval with Hit@5 and MRR, and sent 12 attacks to both models: prompt extraction, jailbreaks, an injected document, and some of my own (a hidden instruction in a chunk, a poisoned policy file, an exfiltration link, German, base64).

Main things I noticed: with only 19 questions no metric showed a clear difference between local and cloud, the ranges are wider than the gaps, while single questions jump by 0.5 or even 1.0. Retrieval is fine at document level (Hit@5 1.00, MRR 0.94 on the 16 labelled questions). Contextual relevancy is low for both (about 0.3), because most of the 5 chunks are not needed. Cloud was much faster (median 1.1 s vs 48.6 s). For security, the local model repeated its system prompt word for word when asked to "repeat the instructions", the cloud model did not. Both models added "Verified by HR-Bot 7" from my hidden instruction, and the cloud one answered "5 days remote" straight from the poisoned file. Azure's content filter blocked 2 of the 12 attacks before they reached the model.

Faithfulness is probably underestimated. `generate.py` shows the model each chunk with a `(source, page N)` label, but `eval_pipeline.py` gives the judge only the chunk text, so correct page and source citations were counted as made up (q02, q03, q11, q12). In q01 the judge also missed that "section 5" is in the chunk itself.

In my own attack 9 a hidden line in a chunk asked for a status image. The cloud model answered the password question correctly and then added a markdown image from `hr-status.example.net` with the user's question in the URL, while the local model ignored it. The URL holds only the question, not document text, but if the answer is shown as markdown the image loads by itself and sends the question to that server.

Results: [day12_capstone](./Day%2012/day12_capstone) · [comparison](./Day%2012/day12_capstone/compare_output.md)

## Day 13

How a ReAct agent works under the hood. Wrote a small tool of my own (`minutes_to_hours`), went through one reason, act, observe, remember loop by hand, then ran a real loop with `gpt-4.1-mini` through the Responses API, where the model picks the tools and stops by calling `final_answer`. Last part: a `search_web` tool with Tavily, so the agent can answer "What is the weather today in Latvia and Lithuania?".

Main things I noticed: on "(100 + 50) * 2, then divide by 3" the model called add and divide in the same step, before it knew what to divide, so `divide(0, 3)` ran for nothing. It still got 100 because it redid the steps in order. With my tool it multiplied 3 × 135 first and then converted 405 minutes into 6 h 45 min without being told the order. For the weather it searched each country separately and answered with Riga 3 °C light rain and Vilnius 4.2 °C rain shower. I cut each search result to 500 characters, otherwise the pages are very long.

Notebook: [Day 13 - Agentic AI and ReAct agents](./Day%2013/Practice%20-%20Agentic%20AI%20and%20ReAct%20Agents%201.ipynb)

## Day 14

Five agent frameworks, one notebook each, all on `gpt-5.4-mini` through Azure: smolagents, LangGraph, LlamaIndex, Google ADK and CrewAI. Every notebook goes through custom tools, an MCP tool and observability, and ends with a challenge that I built: a smart home controller where the thermostat really changes the room temperature, a travel assistant graph, a restaurant agent with booking and a diet filter, a nutrition calculator, and a two-agent casting crew. CrewAI has its own virtual environment because its packages conflict with the others.

Main things I noticed: smolagents writes Python instead of tool calls, but with the default `<code>` tags it often wasted steps. The model sometimes answered without the opening tag, which gives a parsing error and a retry, and once it sent 4 empty code blocks before the real one. With `use_structured_outputs_internally=True` my home agent did each task in one step (about 2 000 input tokens instead of 11 100). In LlamaIndex, `Context(agent)` did not keep the conversation in this version (the course demo forgot the name "Alex"), so I passed a `Memory` object, and then "make it 6 people" booked the right restaurant. The course currency tool returns "1000 EUR = 1000.00 JPY" for a missing rate and the agent repeated it without noticing, so tools should return errors, not fake values. ADK's meal totals matched my own sum of the tool outputs exactly (471.8 kcal), and an unknown food was left out instead of guessed. In CrewAI, asking the casting director for a top 2 ended with "cast nobody" because both were busy, and a sequential crew cannot go back. With a ranked list the coordinator skipped two busy actors and picked the third. The MCP image tool in ADK did not run because Node.js is not installed.

Notebooks: [smolagents](./Day%2014/1.smolagents_practice.ipynb) · [LangGraph](./Day%2014/2.langgraph_practice.ipynb) · [LlamaIndex](./Day%2014/3.llamaindex_practice.ipynb) · [Google ADK](./Day%2014/4.google_adk_practice.ipynb) · [CrewAI](./Day%2014/5.crewai_practice.ipynb)
