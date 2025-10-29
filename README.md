**Time Series Motion Data Classifier for Right and Left Hand Movement (finger-to-nose)**

**General Steps**

1. Input Data Collection
    - Source: IMU data from my phone using the “IMU utility” app
    - Use UDP transfer to laptop for further processing as CSV file
    - Write a python script to host and accept the data packets
    
    (Update: Managed to setup the data pipeline to get data in my PC)
    
2. Data Preprocessing
    - Integrate data from all trials
    - Trim the data points that are out of the trial timestamp
    - Data cleaning by removing unnecessary features from the data
    - Normalize and regularizing the data if necessary
3. Decide on which ML or DL model to use that is suited for time series data classification
    - I am thinking one of the classical ML models would be a good fit considering I wont have that much data to train DL models on.
4. Prepare the data(Train-validation-test split)
5. Model Training
    1. Use google colab
6. Model Testing and fine tuning
    1. Test with friends before.
    

**Possible Problems that may arise(Just predicting at this point)**

1. Getting right formatted data from IMU utility
2. Defining correct sampling frequency
3. IMU allows only UDP data transfer protocol so that is a bit unreliable
4. Deciding which features to use and remove
5. It may be the case that left and right hand movement will not have discernible difference in motion measurement, at least for the sensor in our phones.
6. Not having a controlled environment for train and test data collection
    1. I am thinking of the part of the phone that touches the fixed point in space, and the nose should be exactly the same in all trials and tests so that the data is uniform.

## Next Steps

→ Make the code ready for running trials

→ serialize the files for each trial conducted

→ Stop running the code when UDP disconnects

→ Find a stable way to start and stop the timing so all the timestamps match

→ Do the trials and collect data

→ Understand what each data attribute means and how it contributes to the model training.
