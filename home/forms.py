from django import forms

class MyForm(forms.Form):
    Ticker = forms.CharField(label=False, max_length=8, widget=forms.TextInput(attrs={'placeholder': 'What Stock Do You want to consider', 'style': 'text-align: center;', 'class': 'form-control', 'maxlength':'3'}))
    SMAlength = forms.IntegerField(label=False, required=True,
                                       widget=forms.TextInput(attrs={'placeholder':'SMA Length', 'style': 'text-align: center;', 'class': 'form-control', 'maxlength':'3'}))
