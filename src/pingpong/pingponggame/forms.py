from django import forms

from django.contrib.auth.models import User

from pingponggame.models import *

#Registration form
class PlayerForm(forms.ModelForm):
	class Meta:
		model = Player
		exclude = ('user', 'current_game',)
		widgets = {'image': forms.FileInput()}
		
#User registration form
class UserForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name',)

	def clean_username(self):
		username = self.cleaned_data.get('username')
		if User.objects.filter(username=username):
			raise forms.ValidationError("This user name is already taken!")

		return username

#Get User password
class PasswordForm(forms.Form):
	password = forms.CharField(widget=forms.PasswordInput)
	confirm_password = forms.CharField(widget=forms.PasswordInput)

	def clean(self):
		cleaned_data = super(PasswordForm, self).clean()
		password = cleaned_data.get('password')
		confirm_password = cleaned_data.get('confirm_password')
		if password and confirm_password and password != confirm_password:
			raise forms.ValidationError('Password Not Match.')
		return cleaned_data	

class JoinRoomForm(forms.Form):
	room_id = forms.CharField()

	def clean_room_id(self):
		room_id = self.cleaned_data_get('room_id')
		if not Game.get_by_id():
			raise forms.ValidationError('No such room')
		
		return room_id