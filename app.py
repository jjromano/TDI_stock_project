from flask import Flask, render_template, request, redirect

import requests
import simplejson as json
import pandas as pd  # for DataFrame creation and manipulation
import numpy as np   # np is convention for easy calling, needed for datetime
import os    # pythons operating system for loading/saving files
from pandas.io.json import json_normalize
from bokeh.io import push_notebook, show, output_notebook
from bokeh.layouts import row, gridplot
from bokeh.plotting import figure, show, save, output_file 
from bokeh.embed import components   #needed to produce embedded HTML components for plot
from shutil import copyfile    #needed for copying stocks.html file to templates folder

def get_stock_info(ticker):
    api_key = '5eWyXUgyDyNbYXctVW53'  # static value
    start_date = '2013-01-01'    # needs to be user defined
    end_date = '2017-05-11'      # needs to be user defined
    #ticker = 'FB'                # needs to be user defined
    api_url = "https://www.quandl.com/api/v3/datasets/WIKI/%s/data.json" % ticker
    payload = {'api_key': api_key, 'start_date': start_date, 'end_date': end_date, 'order': 'asc'}
    r = requests.get(api_url, params = payload)
    r_raw = r.json()   
    json_normalize(r_raw)    # Normalize JSON object into flat table
    r_cols = r_raw['dataset_data']['column_names']  # Extract column names
    r_data = r_raw['dataset_data']['data']   # Extract data

    numdays = 3     # needs to measure length
    df = pd.DataFrame(r_data)
    df.columns = r_cols
    return df

#####################################################################
def datetime(x):
    return np.array(x, dtype=np.datetime64)

def output_plot(df, ticker, closing_pr, adj_closing_pr, opening_pr, adj_opening_pr):

    output_notebook()   #set up the bokeh figure
    p1 = figure(x_axis_type="datetime", title="Data from Quandle WIKI set")
    p1.grid.grid_line_alpha=0.3
    p1.xaxis.axis_label = 'Date'
    p1.yaxis.axis_label = 'Price'

    if opening_pr is not None:  #checks if checkbox was checked
        p1.line(datetime(df['Date']), df['Open'], color='#A6CEE3', legend= ticker+':Open')
    if adj_opening_pr is not None:
        p1.line(datetime(df['Date']), df['Adj. Open'], color='#B2DF8A', legend= ticker+':Adj. Open')
    if closing_pr is not None:
        p1.line(datetime(df['Date']), df['Close'], color='#33A02C', legend= ticker+':Close')
    if adj_closing_pr is not None:
        p1.line(datetime(df['Date']), df['Adj. Close'], color='#FB9A99', legend= ticker+': Adj. Close')
    p1.legend.location = "top_left"

    output_file("stocks.html", title="Stock_Info")
    script, div = components(p1)     # returns necessary components to create html plot 
    save(gridplot([[p1]], plot_width=400, plot_height=400))  # saves stocks.html to project folder
    copyfile("stocks.html", "templates/stocks.html")      # creates a copy in the templates folder
    return (script, div)


######################################################################
app = Flask(__name__)

@app.route('/')
def main():
    return redirect('/index')

@app.route('/index',methods=['GET','POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        #request was a POST
        ticker = request.form.get("ticker")    #stock ticker
        closing_pr = request.form.get("closing_pr")    #checkbox inputs from index.html
        adj_closing_pr = request.form.get("adj_closing_pr")
        opening_pr = request.form.get("opening_pr")
        adj_opening_pr = request.form.get("adj_opening_pr")
        df = get_stock_info(ticker)  #dataframe returned with all stock data
        script, div = output_plot(df, ticker, closing_pr, adj_closing_pr, opening_pr, adj_opening_pr)
        return render_template('stocks.html', script=script, div=div)  # added script, div


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')


