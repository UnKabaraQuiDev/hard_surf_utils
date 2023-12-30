def register_handler_if_unregistered(func, handler):
    if not func in handler:
        handler.append(func)

def unregister_handler_if_registered(func, handler):
    if func in handler:
        handler.remove(func)
