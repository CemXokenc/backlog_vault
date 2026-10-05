from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from vault.models import Game


@receiver(pre_save, sender=Game)
def delete_replaced_cover(sender, instance, **kwargs):
    """Remove the old cover file when a game gets another cover."""
    if not instance.pk:
        return
    old_game = Game.objects.filter(pk=instance.pk).first()
    if old_game is None or not old_game.cover:
        return
    if old_game.cover.name != instance.cover.name:
        old_game.cover.delete(save=False)


@receiver(post_delete, sender=Game)
def delete_cover_with_game(sender, instance, **kwargs):
    """Remove the cover file together with the game."""
    if instance.cover:
        instance.cover.delete(save=False)
