import pandas as pd
import joblib 
# from PE_file import pe_data




def tranformer(pe_data):
    data = pd.DataFrame(pe_data,index=[0])
    preprocessor = joblib.load('notebooks_dataset\preprocessor.pkl')

    preprocessed_data = preprocessor.transform(data)
    return preprocessed_data
