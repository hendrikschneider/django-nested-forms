'''A utility for creating mixins dynamically.'''

import functools

class MixinFactory:

    mixin_class = None
    factory_prefix = 'create_'

    def as_mixin(self) -> type:

        prefix_length = len(self.factory_prefix)

        Mixin = type('Mixin', tuple(), {})
        self.mixin_class = Mixin

        attrs = {
            attr_name[prefix_length:]: getattr(self, attr_name)()
            for attr_name in dir(self)
            if attr_name.startswith(self.factory_prefix)
        }

        for attr_name, attr in attrs.items():
            setattr(Mixin, attr_name, attr)

        return Mixin
