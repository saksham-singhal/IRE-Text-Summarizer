#Author: Saksham Singhal
from Stemmer import Stemmer
import sys
import re,os
import math
from collections import defaultdict
from copy import deepcopy
import subprocess

st = Stemmer('english')
pattern=re.compile(r'[\d+\.]*[\d]+|[^\w]+') #pattern to detect numbers (real/integer) non alphanumeric (no underscore)

Summary = []
lamda = 6
alpha  = 0.75
#stopword dictionary from "stopwords.txt" file

stopWordDict = defaultdict(int)
stopWordFile = open("./stopwords.txt","r")
for line in stopWordFile:
	stopWordDict[line.strip()]=1

def extractDocumentCorpus(folder):
	os.chdir(folder)
	print folder
	document_to_senctence_corpus = {}
	for each_file in os.listdir('.'):
		print each_file
		fileptr = open(each_file,'r')
		fileText = fileptr.read()
		l = fileText.split()
		for i in xrange(len(l)):
			if (l[i].count('.')>1) or (not l[i].endswith('.')) :
				l[i] = l[i].replace('.','')
		fileText = " ".join(l)
		fileText = fileText.replace("_"," ")
		fileText = fileText.replace(".","_")
		fileText = re.sub(pattern,' ',fileText)
		fileText = re.sub(r'[\s]+',' ',fileText)
		fileText = fileText.replace('_',".")
	#	print fileText
		fileptr.close()
		if each_file not in document_to_senctence_corpus:
	#		print "yes"
	#		l= fileText.split(".")
			document_to_senctence_corpus[each_file] = fileText
	os.chdir("..")
	return document_to_senctence_corpus

def generateInverseDocFrequency(corpus):
	total_docs = len(corpus.keys())
	idf_scores = defaultdict(float)
	term_doc_count = defaultdict(list)
	for each_doc in corpus:
		current_doc = corpus[each_doc]
		for word in current_doc.split():
			word = word.replace('.','')
			if word not in stopWordDict:
				word = st.stemWord(word)

				#Checking the douments it is belonging to

				if word not in term_doc_count:
					term_doc_count[word] = [each_doc]
				elif each_doc not in term_doc_count[word]:
						term_doc_count[word].append(each_doc)

	for term in term_doc_count:
		idf_scores[term] = math.log10(1+ ((1.0*total_docs)/len(term_doc_count[term])))

	return idf_scores	

def generateClusterInputFile(corpus):
	ClusterInputFile = "../../Temp/SentencesToCluster.txt"
	ClusterInputFile_ptr = open(ClusterInputFile,'w')
	for each_doc in corpus:
		current_doc = corpus[each_doc]
		sentences = []
		sentences = current_doc.split('.')
		print each_doc
		print len(sentences)
	#	break
		for each_sentence in sentences:
			if len(each_sentence)>1:
				if each_sentence[0]==' ':
					each_sentence = each_sentence[1:]
				ClusterInputFile_ptr.write(each_sentence+'\n')

	ClusterInputFile_ptr.close()

def convertFiletoMatFormat():
	os.chdir("../..")
	if not os.path.exists("Temp"):
		os.makedirs("Temp")
	os.system("perl doc2mat/doc2mat -mystoplist=stopwords.txt -nlskip=1 -skipnumeric Temp/SentencesToCluster.txt Temp/ClutoInput.mat")

def clusterSentences(folder):
	line_count = 0
	ClusterFile = open("Temp/SentencesToCluster.txt",'r')
	for line in ClusterFile.readlines():
		line_count+=1
	print line_count	
	os.system("cluto/Linux/vcluster -clmethod=bagglo -sim=cos -niter=100 -seed=45 Temp/ClutoInput.mat "+str(line_count/10))
	os.system("mv ClutoInput.* Temp/")
	return line_count/10
	# Here -clmethod can be replaced with 'direct' for conventional k-Means
	# But in general 'rbr', works for efficiently
	# Limiting maximum number of iteration to 100 and setting similarity to 'cosine'
	# seed determines the start of randomness selection points
	# cstype chooses l2 as clustering criterion.

def mapSentencetoCluster():
	sentenceFile = open("Temp/SentencesToCluster.txt",'r')
	sentences = sentenceFile.readlines()
	sentenceFile.close()

	for idx in range(len(sentences)):
	    sentences[idx] = sentences[idx].split('\n')[0]

	# Creating cluster number index.

	clusterFile = open("Temp/ClutoInput.mat.clustering."+str(noOfClusters),'r')
	clusterIndex = clusterFile.readlines()
	clusterFile.close()

	for idx in range(len(clusterIndex)):
	    clusterIndex[idx] = clusterIndex[idx].split('\n')[0]

	# Merging the 2 together.

	clusterSentenceIndex = []
	for idx in range(len(clusterIndex)):
	    temp = []
	    temp.append(clusterIndex[idx])
	    temp.append(sentences[idx])

	    clusterSentenceIndex.append(temp)

	clusterSentenceIndex.sort()

	# Printing the sentences into the file.
	outputIndexFile= open('Temp/sentence-cluster-sorted-index.txt','w')
	for idx in range(len(clusterSentenceIndex)):
		if int(clusterSentenceIndex[idx][0]) >= 0:			# Handles Unneccesary empty sentences
			line = clusterSentenceIndex[idx][1]+'$'+clusterSentenceIndex[idx][0]+'\n'
			outputIndexFile.write(line)
	outputIndexFile.close()

def consolidateClusters():
	clusterSentencesFile = open('Temp/sentence-cluster-sorted-index.txt','r')
	cluster_to_sentences_dict = defaultdict(list)
	for line in clusterSentencesFile.readlines():
		lin,cluster = line.split('$')
		cluster = cluster.replace('\n','')
		if cluster in cluster_to_sentences_dict:
			cluster_to_sentences_dict[cluster].append(lin)
		else:
			cluster_to_sentences_dict[cluster] = [lin]

	return cluster_to_sentences_dict				

def removeStopWordsandStemming(sentence):
	processed_sentence = []
	for word in sentence:
		if word not in stopWordDict:
			processed_sentence.append(st.stemWord(word))

	return processed_sentence		

def cosine_similarity(sent1,sent2):
	global idf_scores
	cosine_sim_sum = 0.0
	set_sent1 = set(removeStopWordsandStemming(sent1.split()))
	set_sent2 = set(removeStopWordsandStemming(sent2.split()))
	for word in set_sent1:
		if (word in set_sent2) and (word in idf_scores):
			cosine_sim_sum += (sent1.count(word)*sent2.count(word)*idf_scores[word]*idf_scores[word])

	root_sum_sent1 = 0
	root_sum_sent2 = 0
	for word in set_sent1:
		if word in idf_scores:
			root_sum_sent1 += ((sent1.count(word)*idf_scores[word])**2)

	for word in set_sent2:
		if word in idf_scores:
			root_sum_sent2 += ((sent2.count(word)*idf_scores[word])**2)

	root_sum_sent1 = math.sqrt(root_sum_sent1)
	root_sum_sent2 = math.sqrt(root_sum_sent2)
#	print sent1
#	print sent2

	return ((cosine_sim_sum)/(root_sum_sent1*root_sum_sent2))

def calculateSimilarityWithSummary(sentence,summary):
	Summary_similarity = 0
	for i in summary:
		if len(i)>1:
			Summary_similarity += cosine_similarity(sentence,i)

	return Summary_similarity

def calculaterSimilarityWithCorpus(sentence):
	global cluster_to_sentences_dict
	corpus_similarity = 0
	for cluster in cluster_to_sentences_dict:
		current_cluster = cluster_to_sentences_dict[cluster]
		for each_sentence in current_cluster:
			if len(each_sentence)>1:
				corpus_similarity += cosine_similarity(each_sentence,sentence)

	return corpus_similarity		

def getTotalSenteces():
	fp = open('Temp/sentence-cluster-sorted-index.txt','r')
	text = fp.readlines()
	return len(text)

def getDiversity(total_sentences,summary):
	global cluster_to_sentences_dict
	diversity_measure = 0
	for cluster in cluster_to_sentences_dict:
		current_cluster = cluster_to_sentences_dict[cluster]
		intersection_set = set(summary).intersection(set(current_cluster))
		cluster_diversity = 0
		for sentence in intersection_set:
			cluster_diversity += (calculaterSimilarityWithCorpus(sentence)*1.0)/total_sentences

		diversity_measure += math.sqrt(cluster_diversity)

	return diversity_measure		

def getCoverage(summary):
	global cluster_to_sentences_dict
	total_sentences = getTotalSenteces()
	covereage_measure=0
	for cluster in cluster_to_sentences_dict:
		current_cluster = cluster_to_sentences_dict[cluster]
		for each_sentence in current_cluster:
			if len(each_sentence)>1:
				Summary_similarity = calculateSimilarityWithSummary(each_sentence,summary)
				corpus_similarity = calculaterSimilarityWithCorpus(each_sentence)
				covereage_measure += min(Summary_similarity,((alpha*1.0*corpus_similarity)/total_sentences))

	return covereage_measure		

def extractSummary(cluster_to_sentences_dict):
	global Summary
	global lamda
	global alpha
	global current_size

	total_sentences = getTotalSenteces()

	current_sentence = ""
	current_score = 0
	max_sentence = ""
	max_score = 0
	covereage = 0
	max_cluster=-1
	check_cluster=-1
	curent_cov=-1
	current_div=-1
	max_cov=-1
	max_div=-1
	max_sumsin=-1
	max_corsim =-1
	for cluster in cluster_to_sentences_dict:
		current_cluster = cluster_to_sentences_dict[cluster]
	#	print current_cluster
		for each_sentence in current_cluster :
		#	print each_sentence
		#	print Summary
			if (each_sentence not in Summary) and (current_size+len(each_sentence)<665):
		#		print "yes"

				############################## Compute covereage ##############################
	#			current_summary = []
				current_summary = deepcopy(Summary)
				current_summary.append(each_sentence)
			#	print type(each_sentence)
			#	print current_summary

				covereage = getCoverage(current_summary)
			#	summary_sim = calculateSimilarityWithSummary(each_sentence,current_summary)
			#	corpus_sim = calculaterSimilarityWithCorpus(each_sentence)
			#	covereage = min(summary_sim,(alpha*corpus_sim))

				############################### Compute Diversity #############################

				diversity = getDiversity(total_sentences,current_summary)

				############################### Greedily Check ################################

				current_score = covereage + (lamda*diversity)
				current_sentence = each_sentence
				check_cluster =cluster
			#	print" ###################"
			#	print covereage
			#	print diversity
			#	print current_score
			#	print each_sentence
			#	print "###################"
				if current_score > max_score:
					max_score = current_score
					max_sentence = current_sentence
					max_cluster=check_cluster
					max_cov=covereage
					max_div=diversity
				#	max_corsim = corpus_sim
				#	max_sumsin = summary_sim

	Summary.append(max_sentence)
	current_size+=len(max_sentence)
#	print max_score
#	print max_sentence
#	print current_size
#	print max_cluster
#	print max_cov
#	print max_div
#	print max_corsim
#	print max_sumsin
#	print "########################3"
#
current_size =0
main_output_file = open('Final_Output.txt','w')
main_output_file.write('ClusterID\tRouge-1 R\tRouge-1 F\n')
main_output_file.close()
datasetFolder = 'DUC-2004/Cluster_of_Docs'
os.chdir(datasetFolder)
alphatoRouge = defaultdict(float)
alpha = 15
while alpha<35:
	rougue_score=[]
	for cluster in os.listdir('.'):
		current_size=0
		Summary =[]
		if not os.path.exists("../../Temp"):
			os.makedirs("../../Temp")
		document_to_senctence_corpus = extractDocumentCorpus(cluster)
		idf_scores = generateInverseDocFrequency(document_to_senctence_corpus)
		generateClusterInputFile(document_to_senctence_corpus)
		convertFiletoMatFormat()
		noOfClusters = clusterSentences(datasetFolder)
		mapSentencetoCluster()
		cluster_to_sentences_dict = consolidateClusters()
	#	print cluster_to_sentences_dict
		for i in xrange(5):
			extractSummary(cluster_to_sentences_dict)
		outfile = open('Temp/Summaryoutput.txt','w')
		print Summary
		for i in Summary:
			outfile.write(i+'\n')
		outfile.close()
		output = subprocess.check_output("java -cp C_Rouge/C_ROUGE.jar executiverouge.C_ROUGE Temp/Summaryoutput.txt DUC-2004/Test_Summaries/"+cluster+"/ 1 B R",shell=True)
		output = float(output)
		output1 = subprocess.check_output("java -cp C_Rouge/C_ROUGE.jar executiverouge.C_ROUGE Temp/Summaryoutput.txt DUC-2004/Test_Summaries/"+cluster+"/ 1 B F",shell=True)
		output1 = float(output1)
		rougue_score.append(output)
		main_output_file = open("Final_Output.txt",'a')
		main_output_file.write(str(cluster)+"\t"+str(output)+"\t"+str(output1)+"\n")
		print str(cluster)+"\t"+str(output)+"\t"+str(output1)
		main_output_file.close()
		#break

	#	os.system("rm -rf Temp/")
		if not os.path.exists("Temp"):
			os.makedirs("Temp")
		os.chdir(datasetFolder)
	alpha+=10
	alphatoRouge[alpha] = sum(rougue_score)/len(rougue_score)
	print alphatoRouge
	break 
main_output_file.close()
	################################################################
	#														       #
	#			Here we need to start clustering the Docs          #
	# 															   #	
	################################################################


	## Assuming Here basically we have a clustered file which has sentences followed by the cluster they belong in 
	## 	sorted order!.
