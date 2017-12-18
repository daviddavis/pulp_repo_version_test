# Motivation

In order to decide between two different designs in how to handle versioned repositories (one being
a direct relation between repo version and content and the other involving storing the differences
between two versions), we decided to evaluate how PostgreSQL copes with tables that contain billions
of records). We wanted to test what would happen if we had 1 billion associations between repo
versions and content units. How would our PostgreSQL database handle that? Would it be slow? Would
it be large?

# Setup

To get an idea of how a large table of 1 billion records affected performance, I used the existing
code base and instead of dealing with repo versions, I just used repositories. I imagine that the
RepositoryContent model will be replaced with a RepositoryVersionContent model that has the same
fields except repository_version_id instead of repository_id.

We also decided that large repositories like RHEL 7 typically contained about 10,000 units. So to
seed the data, we create 10,000 Content records. With 10,000 Content records, it was necessarily to
create 100,000 repositories since 100,000 times 10,000 is 1 billion. This setup should give us the
same performance as if we had repository versions--we're simply substituting repositories for repo
versions.

# Implementation

I started with first benchmarking some intermediate numbers of repositories before getting to
100,000 repositories (0, 100, ...). For metrics, I looked at how long it took to insert a new
repository with 10,000 repositories, how long it took to read all the content units for an existing
repository, how large the table got, and how big the indexes became (pk, repository_id, content_id,
and repository_id + content_id).

## Hardware

* Vagrant VM with 2 cores
* HDD ~110 MB/s (tested using `dd if=/dev/zero of=speedtest bs=64k count=3200 conv=fdatasync`)
* 12 GB of RAM
* Intel Xeon 4-core E5606 processor

# Results

| Repo Versions | Write (s) | Read (s) | Table (MB) | Index (MB) |
|---------------|-----------|----------|------------|------------|
| 0             | 2.291756  | 0.008121 | 2.3        | 6.5        |
| 100           | 2.182993  | 0.007838 | 74         | 183        |
| 1000          | 2.725601  | 0.005223 | 735        | 1720       |
| 10000         | 55.44191  | 0.006683 | 7309       | 14691      |
| 50000         |
| 100000        |

Note: There are 10,000 repository-version to content associations for each repo version.
