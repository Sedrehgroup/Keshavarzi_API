import factory

from notes.models import Note
from regions.tests.factories import RegionFactory


class NoteFactory(factory.django.DjangoModelFactory):
    region = factory.SubFactory(RegionFactory)
    text = factory.Faker("text", max_nb_chars=200)

    @classmethod
    def create(cls, regions_expert_as_user=False, **kwargs):
        if regions_expert_as_user:
            kwargs['user_id'] = kwargs["region"].expert_id
        else:
            kwargs['user_id'] = kwargs["region"].user_id
        return super(NoteFactory, cls).create(**kwargs)

    class Meta:
        model = Note
