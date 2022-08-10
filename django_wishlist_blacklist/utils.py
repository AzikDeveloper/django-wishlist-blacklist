def get_user_author(user):
    author = getattr(user, "get_binder_author", None)

    if callable(author):
        author = author()

    if author is None:
        author = user

    return author


__all__ = ['get_user_author']
