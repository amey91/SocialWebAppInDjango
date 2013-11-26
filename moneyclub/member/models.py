from django.db import models
import moneyclub.models

# Create your models here.

class UserStockOfInterest(StockOfInterest):
    user=models.ForeignKey(User,blank=False,related_name="user_stock")

    