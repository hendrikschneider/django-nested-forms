'''Helper functions to wrap methods of a Form with
the corresponding methods of the Form's handler.'''

WRAPPER_PREFIX = 'wrap_'
LEN_WRAPPER_PREFIX = len(WRAPPER_PREFIX)

def nest(formset_class, prefix, handler_class):
    '''Return a decorator to nest a formset in a form.'''

    def decorate_class(form_class):
        handler = handler_class(formset_class, prefix)
        for handler_attr_name in dir(handler):
            if not handler_attr_name.startswith(WRAPPER_PREFIX):
                continue
            form_attr_name = handler_attr_name[LEN_WRAPPER_PREFIX:]
            try:
                to_be_wrapped = getattr(form_class, form_attr_name)
            except AttributeError:
                raise AssertionError(
                    'Tried to _ `{form}.{wrapped}` because the handler `{handler}` ' \
                    'has `{wrapper}`, but `{form}.{wrapped}` was not found.'.format(
                        form=form_class.__qualname__,
                        handler=handler_class.__qualname__,
                        wrapped=form_attr_name,
                        wrapper=handler_attr_name,
                    )
                )
            decorated = _wrap(to_be_wrapped, getattr(handler, handler_attr_name))
            setattr(form_class, form_attr_name, decorated)
        return form_class

    return decorate_class

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
