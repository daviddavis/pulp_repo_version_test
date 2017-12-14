import uuid
from datetime import datetime

from pulpcore.app.models import Content, RepositoryContent, Repository

# in order to use our model classes in list comprehensions below and execute this via django shell
globals().update(locals())

CONTENT_COUNT = 10000
REPO_COUNT = 10000


def create_repo_with_contents(units):
    time = datetime.utcnow()
    repo = Repository(name=uuid.uuid1())
    repo.save()

    repo_contents = []
    for content in units:
        repo_contents.append(RepositoryContent(repository=repo,
                                               content=content))
    RepositoryContent.objects.bulk_create(repo_contents)
    print("Add repo time: {t}s".format(t=(datetime.utcnow() - time).total_seconds()))


# SEED DATA

ccount = CONTENT_COUNT - Content.objects.count()
if ccount > 0:
    print("Creating content")
    contents = [Content(type='file') for _ in range(ccount)]
    Content.objects.bulk_create(contents)

contents = Content.objects.all()

rcount = REPO_COUNT - Repository.objects.count()
if rcount > 0:
    print("Creating repos")

    for i in range(rcount):
        print("Creating repo {i} of {total}".format(i=i + 1, total=rcount))
        create_repo_with_contents(contents)

print("Done with setup.")


# TESTS

# insert a single repo

time = datetime.utcnow()
for _ in range(10):
    create_repo_with_contents(contents)
print("Average add repo time: {t}s".format(t=(datetime.utcnow() - time).total_seconds() / 10))

# read a single repo

time = datetime.utcnow()

for _ in range(10):
    repo = Repository.objects.order_by("?").first()
    repo_contents = RepositoryContent.objects.filter(repository_id=repo.id).all()

#print(len(repo_contents))
print("Average read repo contents: {t}s".format(t=(datetime.utcnow() - time).total_seconds() / 10))
