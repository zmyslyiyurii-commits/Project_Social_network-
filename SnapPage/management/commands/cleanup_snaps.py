import os
from django.core.management.base import BaseCommand
from users.models import Snap

class Command(BaseCommand):
    help = 'Фізично видаляє медіафайли переглянутих снапів (status=opened)'

    def handle(self, *args, **options):
        # Шукаємо відкриті снапи, у яких ще є прикріплений файл
        opened_snaps = Snap.objects.filter(status='opened').exclude(media_file='')

        count = 0
        for snap in opened_snaps:
            if snap.media_file and os.path.isfile(snap.media_file.path):
                # Видаляємо файл із диска
                os.remove(snap.media_file.path)
                # Очищаємо поле у БД
                snap.media_file = None
                snap.save(update_fields=['media_file'])
                count += 1

        self.stdout.write(self.style.SUCCESS(f'Успішно видалено {count} медіафайлів переглянутих снапів.'))