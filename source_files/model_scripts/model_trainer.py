import pandas as pd
import joblib 
import pickle
# from PE_file import pe_data
from tensorflow import keras
    
    
    
def trainer(data):
    model = joblib.load('notebooks_dataset\model.pkl')

    predictions = model.predict(data)
    print(predictions)
    # Load the saved model
    loaded_model = keras.models.load_model("notebooks_dataset\my_model.h5")
    pred = loaded_model.predict(data)
    print(pred)
    if predictions >= pred:
        return predictions
    else:
        return pred

