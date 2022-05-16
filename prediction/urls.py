from django.urls import path
from . import views

app_name = "prediction"

urlpatterns = [
    path('', views.predict, name='prediction_page'),
    path('predict/', views.predict_price, name='submit_prediction'),
    path('predict/load_model', views.load_models, name='load_model'),
    path('results/', views.view_results, name='results'),
]
