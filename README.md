# action_recognition data set
https://rose1.ntu.edu.sg/dataset/actionRecognition/ 

## New Approach 1
Frame
- Person Boxes
  - pre-trained detector
- Skeletal Data Detector
  - upper body is enough
- Action Classifier
  - Sequential time data (last 5-10 frames)
  - or single picture
- 1 class per person

## New Approach 2
- transformer

## New Approach 3
- attention layer
