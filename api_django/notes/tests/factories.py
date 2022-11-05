import factory

from notes.models import Note
from regions.tests.factories import RegionFactory


class NoteFactory(factory.django.DjangoModelFactory):
    region = factory.SubFactory(RegionFactory)
    text = factory.Faker("text", max_nb_chars=200)

    class Meta:
        model = Note
