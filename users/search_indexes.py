from haystack.indexes import SearchIndex, CharField, Indexable
from django.contrib.auth.models import User

class UserIndex(SearchIndex, Indexable):
    ''' Index for users created on the site. '''
    text = CharField(document=True, use_template=True)
    first_name = CharField(model_attr='first_name')
    last_name = CharField(model_attr='last_name')
    photo = CharField(indexed=True)

    def get_model(self):
        return User

    def prepare_photo(self, obj):
        try:
            photo_path = str(obj.profilephoto_set.filter(is_set=True)[:1][0].profile_photo)
        except:
            photo_path = '#'
        return photo_path

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(
            is_active=True,
            is_superuser=False,
            is_staff=False
        )
