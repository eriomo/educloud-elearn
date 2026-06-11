"""
Seeds the TopicKeyword table from the built-in keyword lists.

Run automatically on every deploy via build.sh. It is idempotent: it uses
get_or_create, so running it many times never creates duplicates. Once the
rows are in the database (Supabase), a teacher or admin can add, edit, or
deactivate keywords from the Django admin without touching any code.
"""
from django.core.management.base import BaseCommand
from assessments.models import TopicKeyword
from assessments.ml.features import TOPIC_KEYWORDS


class Command(BaseCommand):
    help = 'Seed the TopicKeyword knowledge base from the built-in keyword lists'

    def handle(self, *args, **kwargs):
        created = 0
        existing = 0
        for topic, keywords in TOPIC_KEYWORDS.items():
            for kw in keywords:
                obj, was_created = TopicKeyword.objects.get_or_create(
                    topic=topic,
                    keyword=kw.lower().strip(),
                    defaults={'weight': 1, 'is_active': True},
                )
                if was_created:
                    created += 1
                else:
                    existing += 1
        total = TopicKeyword.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f'Topic keywords seeded. Added {created}, already present {existing}, total in table {total}.'
        ))
