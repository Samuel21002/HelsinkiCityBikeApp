from django.db import models

# CSV fieldnames: FID,ID,Nimi,Namn,Name,Osoite,Address,Kaupunki,Stad,Operaattor,Kapasiteet,x,y
class Station (models.Model):
    
    station_id = models.BigAutoField(primary_key=True)
    fid = models.BigIntegerField(unique=True)
    name_fin = models.CharField(max_length=50)
    name_swe = models.CharField(max_length=50)
    name_eng = models.CharField(max_length=50, default="")
    address_fin = models.CharField(max_length=40)
    address_swe = models.CharField(max_length=40)
    city_fin = models.CharField(null=True, max_length=50)
    city_swe = models.CharField(null=True, max_length=50)
    operator = models.CharField(null=True, max_length=50)
    capacity = models.PositiveSmallIntegerField(null=True)
    geo_pos_x = models.DecimalField(max_digits=8, decimal_places=6)
    geo_pos_y = models.DecimalField(max_digits=8, decimal_places=6)

    def __str__(self):
        return f"'{self.name_fin}, {self.city_fin}'"
    

