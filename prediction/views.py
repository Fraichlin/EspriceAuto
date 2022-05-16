import codecs
import json

import joblib
from django.shortcuts import render
from django.http import JsonResponse
import pandas as pd
from .models import predict_price
import pickle
from esprice import settings
import os
from joblib import load
from catboost import CatBoostRegressor
from catboost import Pool
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import RobustScaler, OneHotEncoder, OrdinalEncoder, StandardScaler
import category_encoders as ce
from sklearn.base import BaseEstimator

base_dir =settings.MEDIA_ROOT
my_file3 = os.path.join(base_dir, str('dataset_no_encoded_no_scaling.csv'))
my_file4 = os.path.join(base_dir, str('final_catboost.joblib'))


df_original = pd.read_csv(my_file3)
df_original2 = pd.read_csv(my_file3)
df_original2.rename(columns={'Power(CV)':'Power', 'Mileage(KM)':'Mileage' ,'Price(TND)':'Price'}, inplace=True)
df_original.rename(columns={'Power(CV)':'Power', 'Mileage(KM)':'Mileage' ,'Price(TND)':'Price'}, inplace=True)
df_original.drop(columns=['Cylinder(L)','Address'],inplace=True)

def predict(request):
    print(df_original.Gearbox.unique())
    marks = df_original.Mark.unique()
    marks = dict(enumerate(sorted(marks), 1))
    years = list(range(1930,2023))
    years = dict(enumerate(years, 1))
    colors = df_original.Color.unique().tolist()
    colors.extend(['violet','orange'])
    colors_sort = sorted(colors)
    colors = dict(enumerate(colors_sort, 1))
    return render(request, 'prediction.html',{'marks':marks.values(),'years':years.values(),'colors':colors.values()})


def robust_scaler(df):
    num_cols = ['Mark_0', 'Mark_1', 'Mark_2', 'Mark_3', 'Mark_4', 'Mark_5', 'Model_0',
       'Model_1', 'Model_2', 'Model_3', 'Model_4', 'Model_5', 'Model_6',  'Model_7', 'Model_8','Year',
            'Energy_0', 'Energy_1','Power','Mileage','Color_2', 'Color_3','Gearbox_0', 'Gearbox_1', 'Gearbox_2']
    label = ['Price']

    X_train = df[num_cols]
    y_train = df['Price']
    X_test = df[num_cols]

    # Scaling & Encoding
    col_transformer = ColumnTransformer([
    ('robust_scaler', RobustScaler(), num_cols)])

    new_col_names = num_cols

    X_train_prepared = pd.DataFrame(col_transformer.fit_transform(X_train, y_train), columns=new_col_names)
    X_val_prepared = pd.DataFrame(col_transformer.transform(X_test.tail(1)), columns=new_col_names)

    return X_val_prepared

def min_max_scaler(val, column):
    list_values = df_original[column].to_list()
    list_values.append(val)
    scaled_value = (val - min(list_values))/(max(list_values) - min(list_values))
    return scaled_value

def predict_price(request):
    if request.POST.get('action') == 'post':
        # Receive data from client

        year = request.POST.get('year')
        if year=='none': year = 0
        else: year = int(year)
        power = request.POST.get('power')
        if power=='none': power = 0
        else: power = int(power)
        mileage = request.POST.get('mileage')
        if mileage=='none': mileage = 0
        else: mileage = int(mileage)
        mark = str(request.POST.get('mark'))
        model = str(request.POST.get('model'))
        color = str(request.POST.get('color'))
        gearbox = str(request.POST.get('gearbox'))
        energy = str(request.POST.get('energy'))

        #encoding data

        #min max scaler
        year_mm = min_max_scaler(year,'Year')
        power_mm = min_max_scaler(power,'Power')
        mileage_mm = min_max_scaler(mileage,'Mileage')


        #binary enconding on categorical feature
        marks = []
        models = []
        years = []
        energies = []
        powers = []
        mileages = []
        colors = []
        gearboxes = []

        marks.append(mark)
        models.append(model)
        years.append(year)
        energies.append(energy)
        powers.append(power)
        gearboxes.append(gearbox)
        mileages.append(mileage)
        colors.append(color)

        df1 = pd.DataFrame(list(zip(marks,models,years,energies,powers,mileages,colors,gearboxes)), columns=['Mark','Model','Year','Energy','Power','Mileage','Color','Gearbox'])
        print(df1)
        df = pd.concat([df_original,df1])
        encoder = ce.BinaryEncoder(cols=['Mark'])
        df = encoder.fit_transform(df)
        encoder = ce.BinaryEncoder(cols=['Model'])
        df = encoder.fit_transform(df)
        encoder = ce.BinaryEncoder(cols=['Energy'])
        df = encoder.fit_transform(df)
        encoder = ce.BinaryEncoder(cols=['Color'])
        df = encoder.fit_transform(df)
        encoder = ce.BinaryEncoder(cols=['Gearbox'])
        df = encoder.fit_transform(df)
        df = df.drop(columns=['Color_0','Color_1','Color_4'],axis = 1)
        print(df.columns)
        final_val = robust_scaler(df)

        # Read model
        ml_model = load(my_file4)

        # Make prediction
        result = ml_model.predict(final_val)
        price = round(result[0])
        print(price)

        # Find the max and the min price
        request_price = df_original.loc[(df_original.Mark==mark) & (df_original.Model==model) & (df_original.Year==year),'Price']
        if not request_price.empty:
            min_price = int(request_price.min())
            max_price = int(request_price.max())
            if min_price < int(request_price.mean()) - 30000:
                min_price = int(request_price.mean()) - 15000
            if max_price > int(request_price.mean()) + 30000:
                max_price = int(request_price.mean()) + 15000
            if price<min_price or price>max_price:
                price = round(request_price.mean())
        else:
            request_price = df_original.loc[(df_original.Mark==mark) & (df_original.Model==model),'Price']
            min_price = int(request_price.min())
            max_price = int(request_price.max())
            if min_price < int(request_price.mean()) - 30000:
                min_price = int(request_price.mean()) - 15000
            if max_price > int(request_price.mean()) + 30000:
                max_price = int(request_price.mean()) + 15000

            if price<min_price or price>max_price:
                price = round(request_price.mean())

        #find similar car ads
        min_ads = price - 10000
        max_ads = price + 10000
        ads = df_original2.loc[(df_original2.Mark==mark) & (df_original2.Model==model)]
        ads_best = ads.loc[(ads.Price > min_ads) & (ads.Price < max_ads),['Mark','Model','Address','Url']].head(3).values.tolist()
        dict_ads = dict(enumerate(ads_best, 1))
        print(dict_ads)
        #predict_price.objects.create(year=year,power=power,mileage=mileage,mark=mark,model=model,color=color,
                                     #gearbox=gearbox,energy=energy,price=result)

        return JsonResponse({'year':year,'power':power,'mileage':mileage,'mark':mark,'model':model,'color':color,
                             'gearbox':gearbox,'energy':energy,'price':price,'min_price':min_price,'max_price':max_price,'ads':dict_ads},
                            safe=False)


def view_results(request):
    # Submit prediction and show all
    data = {"dataset": predict_price.objects.all()}
    return render(request, "result.html", data)



def load_models(request):
     if request.GET.get('action') == 'get':
        mark = str(request.GET.get('mark'))
        models = df_original.loc[df_original.Mark==mark,'Model'].unique()
        dict_models = dict(enumerate(sorted(models), 1))
        return JsonResponse({'models':dict_models,'len':len(dict_models)},safe=False)

