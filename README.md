# TO DO:
Milena:
- hyperparameter tuning weiter machen
- report schreiben (exp 1, 2)

Gwen: 
- run model & save
- eval & visualize
- improve model?

# Dataset 
The preprocessed data is available via One Drive: 

https://1drv.ms/f/c/3c5d2eafc311e6b9/IgBBv41owHx1TIs_KUAPCz55ATC5fNC1SIYtKsirEPiz0Zc?e=SetmlO

Password: SimonSaysPassword  

# action_recognition data set
https://rose1.ntu.edu.sg/dataset/actionRecognition/ 


# experiment 1

sample middle frame -> pre-trained model -> (linear) classifier -> 4 action classes

Usage:
- for every n-th frame in video: 
    is the correct class? 


Pre-trained model:
 - ResNet18?


1. Data Preprocessing:
- get middle frame
- best file format?
- best resolution?
- labels
- split in test and train data

2. Configurate pre-trained model 
- what input is needed?
- what type of output?
- how to continue working with output?

3. train classifier
- with output from model + labels
- (could try different classifier models e.g. knn, DT,...)

4. test
- whole pipeline
- evaluation

5. Optional: Use for simon says case...
- integrate whole architecture for practical use in game
- evaluation of usage
