import factory

from notes.models import Note
from regions.tests.factories import RegionFactory
from users.tests.factories import UserFactory


class NoteFactory(factory.django.DjangoModelFactory):
    region = factory.SubFactory(RegionFactory)
    user = factory.SubFactory(UserFactory)
    text = factory.Faker("text", max_nb_chars=200)

    class Meta:
        model = Note
