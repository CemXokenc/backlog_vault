from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from vault.models import Game, Gamer


def delete_replaced_file(model, instance, field_name):
    """Remove the old file when an object gets another file."""
    if not instance.pk:
        return
    old_object = model.objects.filter(pk=instance.pk).first()
    if old_object is None:
        return
    old_file = getattr(old_object, field_name)
    if old_file and old_file.name != getattr(instance, field_name).name:
        old_file.delete(save=False)


@receiver(pre_save, sender=Game)
def delete_replaced_cover(sender, instance, **kwargs):
    """Remove the old cover file when a game gets another cover."""
    delete_replaced_file(Game, instance, "cover")


@receiver(post_delete, sender=Game)
def delete_cover_with_game(sender, instance, **kwargs):
    """Remove the cover file together with the game."""
    if instance.cover:
        instance.cover.delete(save=False)


@receiver(pre_save, sender=Gamer)
def delete_replaced_avatar(sender, instance, **kwargs):
    """Remove the old avatar file when a gamer uploads another one."""
    delete_replaced_file(Gamer, instance, "avatar")


@receiver(post_delete, sender=Gamer)
def delete_avatar_with_gamer(sender, instance, **kwargs):
    """Remove the avatar file together with the gamer."""
    if instance.avatar:
        instance.avatar.delete(save=False)
