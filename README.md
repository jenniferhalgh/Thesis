# DIT837 Bachelor Thesis

This repository contains five algorithms to support the automated detection of the change types parameter tuning, output data, model structure, input data, and training infrstructure in ML pipelines (based on the change taxonomy by Bhatia et al.). The algorithms are named with their respective change types and can be found inside the folder repomanager. The change types parameter tuning and output data have two algorithms each, in this case parameter_tuning_2.py and output_data_2.py are the latest versions of the algorithms. 

The original dataset can be found in /repomanager/Data/Original Data

The training and testing sets we used can be found in /repomanager/Data. Note that some samples in the training and testing sets were disregarded since they could not be analyzed with our approach.

To test the algorithms, run evaluation.py in repomanager and uncomment the name of the algorithm you want to test. To see the performance of the algorithm, run performance.py in repomanager and uncomment the confusion matrix for the change type you want to evaluate.

