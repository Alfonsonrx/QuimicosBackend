from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _

class UserAccManager(BaseUserManager):
	def create_user(self, email, name, first_lastname, password=None, **extra_fields):
		if not email:
			raise ValueError(_("The Email must be set, its necessary"))

		user = self.model(
			email=email,
			name=name,
			first_lastname=first_lastname,
			**extra_fields
		)
		user.set_password(password)
		user.save()
		return user

	def create_superuser(self, email, name, first_lastname, password=None, **extra_fields):
		extra_fields.setdefault("is_staff", True)
		extra_fields.setdefault("is_superuser", True)

		if extra_fields.get("is_staff") is not True:
			raise ValueError(_("Superuser must have is_staff=True."))
		if extra_fields.get("is_superuser") is not True:
			raise ValueError(_("Superuser must have is_superuser=True."))
		return self.create_user(email, name, first_lastname, password, **extra_fields)
