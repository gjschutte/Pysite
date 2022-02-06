from django.core.exceptions import ValidationError
from django.forms import ModelForm, DateInput
from django.utils.translation import gettext_lazy as _

from route.models import Route, RouteComment, RoutePhoto

class CreateRouteForm(ModelForm):

    # Check if length > 0
    def clean_length(self):
        data = self.cleaned_data['length']

        if data <= 0:
            raise ValidationError(_('Length must be greater than 0.'))
        return data

    class Meta:
        model = Route
        fields = ['name', 'length', 'type', 'province', 'gpx'] 

class CreateRouteCommentForm(ModelForm):

    class Meta:
        model = RouteComment
        fields = ['date', 'comment', 'score']

        widgets = {
            'date': DateInput(format=('%d-%m-%Y'), attrs={'type': 'date'}),
        }

class AddImageForm(ModelForm):
    class Meta:
        model = RoutePhoto
        fields = ['comment', 'image']
