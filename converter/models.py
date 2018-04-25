from django.db import models
from django import forms


# Create your models here.
class UploadFileForm(forms.Form):
    file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    title = forms.CharField()
    # file = forms.FileField()



# most field is stored as json
class BehaviorGraph(models.Model):
    name = models.TextField()
    code = models.TextField() # str
    trace = models.TextField(default=None) # json
    problem_name = models.TextField(null=True) # json
    cog_model = models.TextField(null=True) # json
    var_list = models.TextField(null=True) # json
    brd = models.TextField(null=True) # json

    def __str__(self):
        return self.name


