import factory

from users.models import User


class UserFactory(factory.django.DjangoModelFactory):
    id = factory.Faker("pyint", min_value=0)
    is_active = True
    first_name = factory.Faker("name")
    last_name = factory.Faker("name")
    phone_number = "+989032567181"
    national_code = "0123456789"

    @classmethod
    def create(cls, **kwargs):
        instance: User = super(UserFactory, cls).create(**kwargs)
        instance.set_password(instance.password)
        instance.save(update_fields=["password"])
        return instance

    class Meta:
        model = User


class ExpertFactory(UserFactory):

    @classmethod
    def create(cls, **kwargs):
        instance: User = super(UserFactory, cls).create(**kwargs)
        instance.is_expert = True
        instance.save(update_fields=["is_expert"])
