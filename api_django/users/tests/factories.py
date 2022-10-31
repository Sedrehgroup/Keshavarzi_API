import random

import factory.fuzzy

from users.models import User


class FuzzyPhoneNumber(factory.fuzzy.BaseFuzzyAttribute):
    """Yields random phone number"""

    def fuzz(self):
        pn_list = ["+", "9", "8", "9"]
        for _ in range(0, 9):
            pn_list.append(str(random.randint(0, 9)))
        return ''.join(pn_list)


class UserFactory(factory.django.DjangoModelFactory):
    is_active = True
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    phone_number = FuzzyPhoneNumber()
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
    is_expert = True


class AdminFactory(UserFactory):
    is_superuser = True
    is_staff = True
