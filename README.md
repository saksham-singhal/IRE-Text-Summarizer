# A Reliable Topical Diversity Measure for Text Summarization


### About
+ This project creates a summary (<= 665 bytes) for a given cluster of documents. 
+ The main inspiration for the work [Jeff Bilmes on Class of submodullar functions for document summarization](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.225.4840&rep=rep1&type=pdf)
+ The choice of submodular function lies in their inherent property od **diminishing returns** which suggests that adding content to a subset smaller summary than to a bigger one increases the function value more.
+ I implemented the whole paper and tried to enhance the results by working aroung the clustering techniques.

### Dataset
+ I am using the standard DUC-2004 dataset which is used to test generic multi-document summarization.

### Approaches
+ The first approach basically suggests the exact work done in the papaer by Jeff Bilmes
+ In the second approach we dealt the problem by **_Spectral Clustering_** since I feel that the inherent distribution/shape which the sentences follow should not be disturbed by using partition-based clustering.
+ In the final approach, we approach the problem using another technique on which we fist get the most the similar cluster of sentence and get the best sentence base on the best coverage. We follow on till we have extracted sufficient summary.

### How to Run
+ Running the code is straight forward.

>python <Whichever-Approach>.py

### Tools
+ Many python libraries and dependencies are needed like : sklearn,joblib, muiltiprocessing, PyStemmer, etc,
+ CLUTO for clustering.
+ ROUGE to check the quality of the summaries