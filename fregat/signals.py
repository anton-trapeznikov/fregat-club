from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from fregat.models import MenuItem


@receiver(post_save, sender=MenuItem, dispatch_uid='menu-item-post-save')
def menu_item_post_save(sender, **kwargs):
    instance = kwargs['instance'] if 'instance' in kwargs else None

    if instance and isinstance(instance, MenuItem):
        MenuItem.check_tree()


@receiver(post_delete, sender=MenuItem, dispatch_uid='menu-item-post-delete')
def menu_item_post_delete(sender, **kwargs):
    instance = kwargs['instance'] if 'instance' in kwargs else None
    if instance and isinstance(instance, MenuItem):
        MenuItem.check_tree()