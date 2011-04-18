from django import forms



class SubscribeForm(forms.Form):
	email = forms.EmailField(max_length=255)
