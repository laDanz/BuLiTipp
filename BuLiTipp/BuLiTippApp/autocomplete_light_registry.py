import autocomplete_light
from models import User

class UserAutocomplete(autocomplete_light.AutocompleteModelBase):
	search_fields=['first_name', 'username', 'email']

	def choices_for_request(self):
		if not self.request.user.is_staff:
			self.choices = self.choices.filter(private=False)
		return super(UserAutocomplete, self).choices_for_request()

autocomplete_light.register(User, UserAutocomplete)