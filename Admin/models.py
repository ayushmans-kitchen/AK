from django.db import models

class AdminNotice(models.Model):
    message=models.CharField(max_length=500)
    date=models.DateField(auto_now_add=True)


    def __str__(self):
        return f"{self.message} - {self.date}"
    
    
