from unilex.vocabulary.models import Vocabulary
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model


vocabs = Vocabulary.objects.with_counts().order_by('user', 'title', '-created_at')
dupes = []

prev_user, prev_title, prev_count = None, None, None

for v in vocabs:
    if v.user == prev_user and v.title == prev_title and v.concept_count == prev_count:
        dupes.append(v)
    else:
        prev_user, prev_title, prev_count = v.user, v.title, v.concept_count

for v in dupes:
    print(f'Duplicate: {v.title} by {v.user} ({v.concept_count})')



User = get_user_model()

# Get user IDs that have unverified emails
unverified_users = EmailAddress.objects.filter(verified=False).values_list("user_id", flat=True)
users_with_email = EmailAddress.objects.values_list("user_id", flat=True)
users_with_vocab = Vocabulary.objects.values_list("user_id", flat=True)

# Exclude users who have a Vocabulary entry
users_to_delete1 = User.objects.filter(id__in=unverified_users).exclude(id__in=users_with_vocab)
users_to_delete2 = User.objects.exclude(id__in=users_with_email).exclude(id__in=users_with_vocab)


# Delete the filtered users
deleted_count1, _ = users_to_delete1.delete()
print(f"Deleted {deleted_count1} unverified users without Vocabulary entries.")
deleted_count2, _ = users_to_delete2.delete()
print(f"Deleted {deleted_count2} users without email without Vocabulary entries.")
