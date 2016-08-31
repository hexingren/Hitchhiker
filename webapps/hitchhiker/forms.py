#!/usr/bin/python
from django import forms
from django.contrib.auth.models import User
from hitchhiker.models import *
from django.core.validators import validate_email, RegexValidator

"""
class AuthenticationForm(forms.Form):
	username = forms.CharField(
		max_length = 20,
		label='Username',
		validators = [RegexValidator(r'^[0-9a-zA-Z]*$',
					  message='Enter only letters and numbers')],
		widget=forms.TextInput(attrs={'class' : 'form-control', 
		  							  'placeholder' : 'Username',
		  							  }),
	)
	password = forms.CharField(
		max_length = 20,
		label='Password',
		widget=forms.PasswordInput(attrs={'class' : 'form-control', 
		  							   'placeholder' : "Your Password",
		  							  }),
	)
"""


class RegisterForm(forms.Form):
	firstname = forms.CharField(
		max_length = 20,
		label='First Name',
		required = False,
		widget=forms.TextInput(attrs={'class' : 'form-control', 
									  'placeholder' : 'First Name',
									  'id' : 'inputFirstName'
							          'autofocus',
									  }),
    )
	lastname = forms.CharField(
		max_length = 20,
		label='Last Name',
		required = False,
		widget=forms.TextInput(attrs={'class' : 'form-control', 
		  							  'placeholder' : 'Last Name',
		  							  'id' : 'inputLastName'
          							  'autofocus',
		  							  }),
    )
	email = forms.CharField(
		max_length = 50,
		validators = [validate_email],
		widget=forms.EmailInput(attrs={'class' : 'form-control', 
		  							  'placeholder' : 'Your Email',
		  							  'id' : 'inputEmail'
          							  'autofocus',
		  							  }),
	)
	
	username = forms.CharField(
		max_length = 20,
		label='Username',
		validators = [RegexValidator(r'^[0-9a-zA-Z]*$',
					  message='Enter only letters and numbers')],
		widget=forms.TextInput(attrs={'class' : 'form-control', 
		  							  'placeholder' : 'Username',
		  							  'id' : 'inputUsername'
          							  'autofocus',
		  							  }),
	)
	age = forms.IntegerField(
		label='Age',
		required = False,
		widget=forms.NumberInput(attrs={'class' : 'form-control', 
		  							   'placeholder' : '0',
										'min' : "0", 
										'max' : "200",
		  							   'id' : 'inputAge',
										}),
	)
	bio = forms.CharField(
		max_length = 430,
		label='Bio',
		required = False,
		widget=forms.Textarea(attrs={'class' : 'form-control', 
		  							   'placeholder' : "I'm a",
		  							   'id' : 'inputBio',
		  							  }),
		
	)
	password1 = forms.CharField(
		max_length = 20,
		label='Password',
		widget=forms.PasswordInput(attrs={'class' : 'form-control', 
		  							   'placeholder' : "Your Password",
		  							   'id' : 'inputPassword'
          							   'autofocus',
		  							  }),
	)
	password2 = forms.CharField(
		max_length = 20,
		label='Confirm Password',
		widget=forms.PasswordInput(attrs={'class' : 'form-control', 
		  							   'placeholder' : "Confirm Password",
		  							   'id' : 'confirmPassword'
          							   'autofocus',
		  							  }),
	)
	
	def clean(self):
		cleaned_data = super(RegisterForm, self).clean()
		password1 = cleaned_data.get('password1')
		password2 = cleaned_data.get('password2')
		if password1 and password2 and password1 != password2:
			raise forms.ValidationError("Passwords do not match.")
		
		userAge = cleaned_data.get('age')
		if (userAge < 0 or userAge > 150) and (userAge != None): #if use (userAge != None): NOT NULL constraint failed: socialnetwork_profile.age
			raise forms.ValidationError("Age is invalid.")
		return cleaned_data
	
	def clean_username(self):
		username = self.cleaned_data.get('username')
		if User.objects.filter(username__exact=username):                 # hren
			raise forms.ValidationError("Username is already taken.")
		return username
		
class EditProfileForm(forms.ModelForm):
	class Meta:
		model = Profile
		exclude = (
			'user',
			'friends',
			'pictureUrl',
			'destinations',
			'messages',
		)
		widgets = {'picture': forms.FileInput()} # prevent the user from deleting avater
	picture = forms.FileField(required=False, label='Change picture')
		
		
	def __init__(self, *args, **kwargs):
		super(EditProfileForm, self).__init__(*args, **kwargs)
		self.fields['lName'].label = 'Last Name'
		self.fields['lName'].widget = forms.TextInput(attrs={'class': "form-control"})
		self.fields['fName'].label = 'First Name'
		self.fields['fName'].widget = forms.TextInput(attrs={'class': "form-control"})
		self.fields['age'].widget = forms.NumberInput(attrs={'class': "form-control"})
		self.fields['shortBio'].label = 'Short Bio'
		self.fields['shortBio'].widget=forms.Textarea(attrs={'class': "form-control"})
		self.fields['email'].widget = forms.EmailInput(attrs={'class': "form-control"})
	
	def clean(self):
		cleaned_data = super(EditProfileForm, self).clean()
		userAge = cleaned_data.get('age')
		if (userAge < 0 or userAge > 200) and (userAge != None): # hren
			raise forms.ValidationError("Age is invalid.")
		userEmail = cleaned_data.get('email')
		if userEmail != '' and not '@' in userEmail:
			raise forms.ValidationError("")
		return cleaned_data
