from django import forms

from django.contrib.auth.models import User

from pingponggame.models import *

#Registration form
class RegistrationForm(forms.ModelForm):
	class Meta:
		model = Player
		exclude = ('user', 'current_game')
	# username = forms.CharField()
	# firstname = forms.CharField()
	# lastname = forms.CharField()
	# password = forms.CharField(widget=forms.PasswordInput)
	# confirmpassword = forms.CharField(widget=forms.PasswordInput)


	def clean_bio(self):
		userbio = self.cleaned_data.get('bio')
		if len(userbio)>200:
			raise forms.ValidationError("Your bio should not be longer than 200")
		return userbio

	# #validation of common fields
	# def clean(self):
	# 	cleaned_data = super(RegistrationForm, self).clean()

	# 	#Conforms the two passwords typed in are the same
	# 	password = cleaned_data.get('password')
	# 	confirmpassword = cleaned_data.get('confirmpassword')
	# 	if password and confirmpassword and password != confirmpassword:
	# 		raise forms.ValidationError("Passwords do not match")

	# 	return cleaned_data

	# def clean_username(self):
	# 	username = self.cleaned_data.get('username')
	# 	if User.objects.filter(username=username):
	# 		raise forms.ValidationError("This user name is already taken")

	# 	return username


# #User Profile form
# class UserProfile(models,Model):
# 	user = models.ForeignKey(User, related_name = 'owner')
# 	age = models.IntegerField(default=0, blank = True)
# 	bio = models.CharField(default = '', max_length=1000, blank = True)
# 	image = models.ImageField(upload_to = "userpictures" ,  blank = True)
# 	firstname = models.CharField(default = '', max_length=40, blank = True)
# 	lastname = models.CharField(default = '', max_length=40, blank = True)
# 	password = models.CharField(default = '', max_length=40, blank = True)
# 	email = models.EmailField(blank = True)	

#User registration form
class UserForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name',)

	def clean_username(self):
		username = self.cleaned_data.get('username')
		if User.objects.filter(username=username):
			raise forms.ValidationError("This user name is already taken！")

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
