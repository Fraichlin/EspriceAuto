from django.db import models


class predict_price(models.Model):

    mark_0 = models.FloatField()
    mark_1 = models.FloatField()
    mark_2  = models.FloatField()
    mark_3  = models.FloatField()
    mark_4  = models.FloatField()
    model_0  = models.FloatField()
    model_1  = models.FloatField()
    model_2  = models.FloatField()
    model_3  = models.FloatField()
    model_4  = models.FloatField()
    model_5  = models.FloatField()
    model_6  = models.FloatField()
    model_7  = models.FloatField()
    model_8  = models.FloatField()
    color_2 = models.FloatField()
    color_3 = models.FloatField()
    power = models.FloatField()
    year = models.FloatField()
    mileage = models.FloatField()
    energy_0 = models.FloatField()
    energy_1 = models.FloatField()
    gearbox_0 = models.FloatField()
    gearbox_1 = models.FloatField()
    gearbox_2 = models.FloatField()
    price = models.FloatField()

    def __str__(self):
        return self.classification
