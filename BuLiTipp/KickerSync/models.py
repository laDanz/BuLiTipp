from django.db import models

# Create your models here.
class SpieltagXMLData(models.Model):
	class Meta:
		app_label = 'KickerSync'
	datum = models.DateTimeField(auto_now_add=True)
	xmldata = models.CharField(max_length=3000)
	spieltagid = models.IntegerField()