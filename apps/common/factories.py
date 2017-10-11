from apps.profile.models import Profile
from apps.role.models import Role
from apps.user.models import User


class Person(object):
    pass


def create_person(
    email='john.smith@example.com',
    first_name="my first name",
    last_name="my last name"
):
    user = User.objects.create_user(
        email=email,
        password="password",
        first_name=first_name,
        last_name=last_name,
    )
    profile = Profile.objects.create(user=user)

    role = Role.objects.create(author=user)

    person = Person()

    person.user = user
    person.user.password = "password"

    person.profile = profile

    person.role = role

    return person
