import autocomplete_light
from models import User

class UserAutocomplete(autocomplete_light.AutocompleteModelBase):
	search_fields=['first_name', 'username', 'email']
	limit_choices = 5
	def choices_for_request(self):
		query = self.request.GET["q"]
		# query only with at least 3 characters, privacy
		if len(query)<3:
			return []
		return super(UserAutocomplete, self).choices_for_request()

autocomplete_light.register(User, UserAutocomplete)