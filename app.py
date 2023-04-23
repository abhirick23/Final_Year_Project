from flask import Flask, render_template,request
import pandas as pd
import numpy as np

import os

from source_files.model_scripts.PE_file import func

from source_files.model_scripts.data_transformer import tranformer
from source_files.model_scripts.model_trainer import trainer


application = Flask(__name__)


app = application

@app.route('/')
def index():
    return render_template('home.html')


@app.route('/predictdata',methods=['GET','POST'])
def predict_datapoint():
    if request.method == 'GET':
        return render_template('home.html')
    else:
        file = request.files["input_file"]
        file_path = os.path.join("D:\Final_Year_Project\PE_files",file.filename)
        file.save(file_path)
        
        data  =  func(file_path)
        # print(data)
        transformed_data = tranformer(data)
        
        results = trainer(transformed_data)
        
        return render_template('index.html',results = results)

if __name__=="__main__":
    app.run(host = '0.0.0.0',debug=True)