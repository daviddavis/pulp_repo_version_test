import uuid
from datetime import datetime
from django.db import connection

from pulpcore.app.models import Content, RepositoryContent, Repository

# in order to use our model classes in list comprehensions below and execute this via django shell
globals().update(locals())

CONTENT_COUNT = 10000
REPO_COUNT = 1000
DROP_INDEXES = True
SAMPLE_SIZE = 100


def drop_repo_content_indexes():
    query = """
        DO
        $$BEGIN
            EXECUTE (
                SELECT 'ALTER TABLE '||table_name||' DROP CONSTRAINT '||constraint_name||''
                FROM information_schema.constraint_table_usage
                WHERE table_name = 'pulp_app_repositorycontent' AND constraint_name NOT ILIKE '%pkey'
            );

            EXECUTE (
                SELECT 'DROP INDEX ' || string_agg(indexrelid::regclass::text, ', ')
                FROM   pg_index  i
                WHERE  i.indrelid = 'pulp_app_repositorycontent'::regclass AND indisprimary IS FALSE
            );
        END$$;
    """
    with connection.cursor() as cursor:
        cursor.execute(query)


def recreate_repo_content_indexes():
    query = """
        ALTER TABLE pulp_app_repositorycontent ADD UNIQUE (content_id, repository_id);
        CREATE INDEX ON pulp_app_repositorycontent (content_id);
        CREATE INDEX ON pulp_app_repositorycontent (repository_id);
     """
    with connection.cursor() as cursor:
        cursor.execute(query)


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

if DROP_INDEXES:
    drop_repo_content_indexes()

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

if DROP_INDEXES:
    recreate_repo_content_indexes()

print("Done with setup.")


# TESTS

# insert a single repo

time = datetime.utcnow()
for _ in range(SAMPLE_SIZE):
    create_repo_with_contents(contents)
print("Average add repo time: {t}s".format(t=(datetime.utcnow() - time).total_seconds() / SAMPLE_SIZE))

# read a single repo

time = datetime.utcnow()

for _ in range(SAMPLE_SIZE):
    repo = Repository.objects.order_by("?").first()
    repo_contents = RepositoryContent.objects.filter(repository_id=repo.id).all()

#print(len(repo_contents))
print("Average read repo contents: {t}s".format(t=(datetime.utcnow() - time).total_seconds() / SAMPLE_SIZE))
