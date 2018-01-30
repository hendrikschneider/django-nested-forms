'''Helper functions to wrap methods of a Form with
the corresponding methods of the Form's handler.'''

class ExtraTaskAttacher:

    '''Decorator factory to insert extra tasks before and after method calls.'''

    wrapper_prefix = 'wrap_'
    len_wrapper_prefix = len(wrapper_prefix)

    def __call__(self, wrapped_class):
        '''Wrap methods in wrapped_class with corresponding wrapper in self.'''
        for self_attr_name in dir(self):
            if not self_attr_name.startswith(self.wrapper_prefix):
                continue
            wrapped_attr_name = self_attr_name[self.len_wrapper_prefix:]
            try:
                to_be_wrapped = getattr(wrapped_class, wrapped_attr_name)
            except AttributeError:
                raise AssertionError(
                    'Tried to wrap `{form}.{wrapped}` because the handler `{handler}` ' \
                    'has `{wrapper}`, but `{form}.{wrapped}` was not found.'.format(
                        form=wrapped_class.__qualname__,
                        handler=self.__class__.__qualname__,
                        wrapped=wrapped_attr_name,
                        wrapper=self_attr_name,
                    )
                )
            decorated = _wrap(to_be_wrapped, getattr(self, self_attr_name))
            setattr(wrapped_class, wrapped_attr_name, decorated)
        return wrapped_class


def _wrap(main_func, wrapper_func):
    '''Ensure `main_func` to do extra tasks before and after it is called.

    `main_func` is the function to be decorated.

    `wrapper_func` should be a coroutine function
    with exactly one yield statement.
    '''

    def wrapped(*args, **kwargs):
        # prepare coroutine
        wrapper_coroutine = wrapper_func(*args, **kwargs)

        next(wrapper_coroutine)
        main_func_return = main_func(*args, **kwargs)

        try:
            wrapper_coroutine.send(main_func_return)

        except StopIteration as stop_iter:
            # StopIteration should be raised here.
            return stop_iter.value

        else:
            # If StopIteration is not raised, that's an error.
            raise AssertionError(
                'Wrappers in handlers should `yield` exactly one time, ' \
                'on the timing that it wants the wrapped function to be called, ' \
                'but `{}` seems to `yield` multiple times.'.format(
                    wrapper_func.__qualname__
                )
            )

    return wrapped
