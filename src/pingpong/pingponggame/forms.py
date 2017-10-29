from django import forms

from django.contrib.auth.models import User

from pingponggame.models import *

#Registration form
class RegistrationForm(forms.ModelForm):
	class Meta:
		model = Player
		exclude = ('user', 'current_game')

	def clean_bio(self):
		userbio = self.cleaned_data.get('bio')
		if len(userbio)>200:
			raise forms.ValidationError("Your bio should not be longer than 200")
		return userbio

#User registration form
class UserForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name',)

#Get User password
class PasswordForm(forms.Form):
	password = forms.CharField(widget=forms.PasswordInput)
	confirm_password = forms.CharField(widget=forms.PasswordInput)

	def clean(self):
		cleaned_data = super(PasswordForm, self).clean()
		password = cleaned_data.get('password')
		confirm_password = cleaned_data.get('confirmed_password')
		if password and confirm_password and password != confirm_password:
			raise forms.ValidationError('Password Not Match.')
		return cleaned_data	
