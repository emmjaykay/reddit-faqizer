# Reddit Faqizer

How do you get a computer to recognize that two questions like the following:

    'Why just almost anything, what are you hiding?..',
    'Why *almost* anything? What are you hiding?'
    
Are actually the same question? Fortunately, I have a solution!

This is a simple prototype to find the duplicate questions in a reddit AMA. It's goal is to make question-answering easier for interviewees by
 * saving time from having to answer questions over and over again,
 * as well as for the Reddit AMA audience who can have more of their questions answered.
 
#### How it works 

First questions are parsed from the Reddit API or a pickle file, then questions are broken down into their individual words, followed by the removal of *stopwords* (words that are so common that they are not helpful, such as 'the'), then to be translated into a mathematical representation using something called *Term Frequency, Inverse Document Frequency*, and then finally, taking that representation and finding which questions had the most likely chance of being duplicates.

## Getting The Data

I use praw to collect data from the reddit API. From there, I pick out comments that are top level questions as candidates to be tested for duplicates. For my experiment, I used the recent [Amy Poehler AMA](http://www.reddit.com/r/IAmA/comments/2kp7w0/im_amy_poehler_amaa/) 

## TFIDF and n-grams

An n-gram of a sentence is like a moving window over a word.

     This is a sentence
could become

     this is
     this is a
     is a sentence
     a sentence
     
Sometimes you can have what is called a skip n-gram, which would be like

     this is
     this a
     this is a
     this is sentence
     this a sentence

A TFIDF score is given to each word or n gram in a linear algebra matrix representation. The individual cells in a matrix are now replaced with TFIDF scores.

#### How to calculate a TFIDF score

TFIDF has two parts, *term frequency* and *inverse document frequency*. The basic strategy is to give points for how often a term appears in a sentence and take away points if it appears often through out all the sentences you have. I quote [tfidf.com](http://www.tfidf.com/)

      Consider a document containing 100 words wherein the word cat
	  appears 3 times. The term frequency (i.e., tf) for cat is
	  then (3 / 100) = 0.03. Now, assume we have 10 million documents
	  and the word cat appears in one thousand of these. Then, the
	  inverse document frequency (i.e., idf) is calculated
	  as log(10,000,000 / 1,000) = 4. Thus, the Tf-idf weight is
	  the product of these quantities: 0.03 * 4 = 0.12.

###Deducing duplicates      
We use a machine learning technique called [cluster analysis](http://en.wikipedia.org/wiki/Cluster_analysis). Specifically, we use a clustering algorithm called DBSCAN. The nice thing about this is that we don't have to know ahead of time how many clusters of duplicate questions that exist in our corups.

The end result can be seen in [here](sample.output).
 
