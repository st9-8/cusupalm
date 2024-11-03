from django.db import models


class CustomEnum(object):
    class Enum(object):
        name = None
        value = None
        type = None

        def __init__(self, name, value, c_type):
            self.name = name
            self.value = value
            self.type = c_type

        def __str__(self):
            return self.name

        def __repr__(self):
            return self.name

        def __eq__(self, other):
            if other is None:
                return False
            if isinstance(other, CustomEnum.Enum):
                return self.value == other.value
            raise TypeError

    @classmethod
    def choices(cls):
        attrs = [a for a in cls.__dict__.keys() if a.isupper()]
        values = [
            (cls.__dict__[v], CustomEnum.Enum(v, cls.__dict__[v], cls).__str__())
            for v in attrs
        ]
        return sorted(values, key=lambda x: x[0])

    @classmethod
    def default(cls):
        """
        Returns default value, which is the first one by default.
        Override this method if you need another default value.
        """
        return cls.choices()[0][0]

    @classmethod
    def get(cls, value):
        try:
            if type(value) is int:
                return [
                    CustomEnum.Enum(k, v, cls)
                    for k, v in cls.__dict__.items()
                    if k.isupper() and v == value
                ][0]
            key = value.upper()
            return CustomEnum.Enum(key, cls.__dict__[key], cls)
        except Exception:
            return None

    @classmethod
    def key(cls, key):
        try:
            return [value for name, value in cls.__dict__.items() if name == key.upper()][
                0
            ]
        except Exception:
            return None

    @classmethod
    def get_counter(cls):
        return {value: 0 for key, value in cls.__dict__.items() if key.isupper()}

    @classmethod
    def items(cls):
        attrs = [a for a in cls.__dict__.keys() if a.isupper()]
        values = [(v, cls.__dict__[v]) for v in attrs]
        return sorted(values, key=lambda x: x[1])

    @classmethod
    def is_valid_transition(cls, from_status, to_status):
        return from_status == to_status or from_status in cls.transition_origins(
            to_status
        )

    @classmethod
    def transition_origins(cls, to_status):
        return cls._transitions[to_status]

    @classmethod
    def get_name(cls, key):
        choices_name = dict(cls.choices())
        return choices_name.get(key)

    @classmethod
    def display(cls):
        attrs = [a for a in cls.__dict__.keys() if a.isupper()]
        return ', '.join(attrs)


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def save(
            self,
            *args,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None,
    ):
        self.full_clean()
        super().save(*args,
                     force_insert=False,
                     force_update=False,
                     using=None,
                     update_fields=None, )
