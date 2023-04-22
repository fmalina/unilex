from unilex.vocabulary.models import Vocabulary


vocabs = Vocabulary.objects.with_counts().order_by('user', 'title', '-created_at')
dupes = []

prev_user, prev_title, prev_count = None, None, None

for v in vocabs:
    if v.user == prev_user\
            and v.title == prev_title\
            and v.concept_count == prev_count:
        dupes.append(v)
    else:
        prev_user, prev_title, prev_count = v.user, v.title, v.concept_count

for v in dupes:
    print(f"Duplicate: {v.title} by {v.user} ({v.concept_count})")
