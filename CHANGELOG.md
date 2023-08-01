# CHANGELOG



## v0.26.0 (2023-08-01)

### Ci

* ci: Update semantic release config ([`d7f778b`](https://github.com/Sieboldianus/lbsntransform/commit/d7f778b9d8672439e0307db27185062217ff0a60))

### Documentation

* docs: Add currently supported Mappings to documentation intro ([`ada73aa`](https://github.com/Sieboldianus/lbsntransform/commit/ada73aad4407bf6763aaf180181d07bffc0d8a97))

### Feature

* feat: Add mapping for iNaturalist gbif data

This mapping adds a mapping to lbsntransform for the iNaturalist gbif CSV data format [1]. Some opinionated decisions are made in the mapping, (1) species names are mapped to lbsn post_filter; (2) kingdom is mapped to topic_group, and (3) occurrences that match known emoji are added to the lbsn emoji list. \n[1]: https://www.gbif.org/dataset/50c9509d-22c7-4a22-a47d-8c48425ef4a7 ([`02368df`](https://github.com/Sieboldianus/lbsntransform/commit/02368dffd1896dadf9bc3441c52d9714da590506))

### Fix

* fix: If source_web is True, input_path expects a List[str] ([`a1339b1`](https://github.com/Sieboldianus/lbsntransform/commit/a1339b1d524836738a3e0d73e582e20fd06d01e4))

* fix: --use_csv_dictreader not working when input source is url ([`2f04251`](https://github.com/Sieboldianus/lbsntransform/commit/2f0425106d3df4305a312a8aa27e6a94046d410b))

### Refactor

* refactor: Improve datetime parsing ([`2449044`](https://github.com/Sieboldianus/lbsntransform/commit/2449044f2e7388a0d6b4642b1a52357bd6ea85aa))

* refactor: Use kwargs for repeated attrs ([`8265985`](https://github.com/Sieboldianus/lbsntransform/commit/82659853745373b7edd83e1486ec55072a1014ab))

### Style

* style: Minor code formatting ([`244b9d6`](https://github.com/Sieboldianus/lbsntransform/commit/244b9d60b5bf7e38cd53bb062b0e6bcae0f5e6c6))

### Unknown

* Merge branch &#39;feat-inaturalist&#39; into &#39;master&#39;

fix: If source_web is True, input_path expects a List[str]

See merge request lbsn/lbsntransform!18 ([`b56ec2c`](https://github.com/Sieboldianus/lbsntransform/commit/b56ec2c411765cde20fbf5441702d4e4beb2aac4))

* Merge branch &#39;feat-inaturalist&#39; into &#39;master&#39;

feat: Add mapping for iNaturalist gbif data

See merge request lbsn/lbsntransform!17 ([`9d3f2d7`](https://github.com/Sieboldianus/lbsntransform/commit/9d3f2d7cb1266f32294ca462a949a2b33803efd9))

* tests: Add iNaturalist gbif integration test ([`23cc9f2`](https://github.com/Sieboldianus/lbsntransform/commit/23cc9f29a02b95528eadcab0a3459b08b69068d8))

* mappings: Use lower case for topic_group attribute ([`a008360`](https://github.com/Sieboldianus/lbsntransform/commit/a008360f2c72f51d13d44b7b42f613fc508ec33d))


## v0.25.1 (2023-05-16)

### Fix

* fix: TypeError for unhashable type: &#39;CompositeKey&#39; (lazy-initialized) ([`68fd9c5`](https://github.com/Sieboldianus/lbsntransform/commit/68fd9c5e020a0636a477ef8dc5933d7329d69c64))

### Unknown

* mappings: Capture media-oembed NoneType ([`40ec1a0`](https://github.com/Sieboldianus/lbsntransform/commit/40ec1a0acb6b46635c458496cc8b54d0111f1997))

* mappings: Reddit capture NoneType for media_type ([`b1412d5`](https://github.com/Sieboldianus/lbsntransform/commit/b1412d5d80674b2183ab29ca74f96d51693bf3e5))

* mappings: Fix wrong referencedPost_pkey in comment processing ([`2410fae`](https://github.com/Sieboldianus/lbsntransform/commit/2410faec8878dfaef07add077f363e83196d4042))

* mappings: Fix reddit mapping submitting both Post and PostReaction for the same reference ([`b996489`](https://github.com/Sieboldianus/lbsntransform/commit/b9964892ba36ba79b7de1ee8133125393ba979a3))


## v0.25.0 (2023-05-15)

### Chore

* chore: Use commit as version source for python-semantic-release ([`0c49de7`](https://github.com/Sieboldianus/lbsntransform/commit/0c49de7dd5de4cc3b78f465794e074e2415f7039))

### Ci

* ci: Activate tests on all branches ([`a32b3f1`](https://github.com/Sieboldianus/lbsntransform/commit/a32b3f1aa697ece4ce0217f15041b1a97dba01cf))

* ci: Remove duplicate install ([`8300c73`](https://github.com/Sieboldianus/lbsntransform/commit/8300c73a69f493146c2b484a9a19d1881ed41f0c))

* ci: Fix gitlab docker runner connection to lbsn-rawdb-test (docker network) ([`b8e0fbe`](https://github.com/Sieboldianus/lbsntransform/commit/b8e0fbedd6ea28c9d411e3bac1a97304acfd5fba))

* ci: Fix nltk not installed ([`9e681e0`](https://github.com/Sieboldianus/lbsntransform/commit/9e681e07fd50e86a69b5dabe12ebf2b993e34084))

* ci: Fix argdown ([`c559e58`](https://github.com/Sieboldianus/lbsntransform/commit/c559e5855aa2be8fa9b96c62634c19643645faeb))

* ci: Disable releasing on development branches ([`5e38bdf`](https://github.com/Sieboldianus/lbsntransform/commit/5e38bdf0f87fd7bf447cbc122e9bfe608f8f8e0c))

* ci: Split release stage into test and artifacts, add pip caching ([`ba0ef47`](https://github.com/Sieboldianus/lbsntransform/commit/ba0ef47e23aaf970c69c23247a889729d47b3d49))

### Feature

* feat: Add mapping for Reddit comments and submissions ([`a665e9d`](https://github.com/Sieboldianus/lbsntransform/commit/a665e9da27b647c9e685f81b7b13a4f488268598))

* feat: Add new topic_group and post_downvotes attribute ([`12c6bbb`](https://github.com/Sieboldianus/lbsntransform/commit/12c6bbbf1db520fe456ffa04bc657111785230cb))

* feat: Allow handing pre-defined BaseConfig to main() ([`14549d9`](https://github.com/Sieboldianus/lbsntransform/commit/14549d954f2102cbc7a5d4bcb9471551600aeec9))

### Fix

* fix: Report package version without package name ([`94081e0`](https://github.com/Sieboldianus/lbsntransform/commit/94081e0e0bc92cdd79edfb077f5c79ff0b7861f9))

### Refactor

* refactor: Significant refactor for Hashtag, @-Mention and UserMention in HelperFunctions ([`ead9afb`](https://github.com/Sieboldianus/lbsntransform/commit/ead9afbfd213079a55dee1530a74c1e1284f21e8))

* refactor: Remove complicated ProtoCompositeContainer check, replace with simple length-check ([`33251be`](https://github.com/Sieboldianus/lbsntransform/commit/33251be4c32eed91d4214d23faf512791497af0b))

* refactor: Update standard lbsnmapping - simplify header ([`7bf1d55`](https://github.com/Sieboldianus/lbsntransform/commit/7bf1d55bd60d448ea76d50b306e75407717fafb8))

* refactor: Simplify handling of unused args and kwargs in mappings ([`8bec334`](https://github.com/Sieboldianus/lbsntransform/commit/8bec334a92b8247e5eab9d175313c1fa7ca20aaf))

* refactor: Handling of mapping-arguments as kwargs and args ([`04241da`](https://github.com/Sieboldianus/lbsntransform/commit/04241dad41f7ca4af29654eab842721d477141bc))

### Style

* style: Refactor code style ([`53214be`](https://github.com/Sieboldianus/lbsntransform/commit/53214be4131f91ab4bb92089c2f9b1caaf7e7579))

### Unknown

* Merge branch &#39;reddit-mapping&#39; into &#39;master&#39;

feat: Add Reddit mapping

See merge request lbsn/lbsntransform!16 ([`5d65ffc`](https://github.com/Sieboldianus/lbsntransform/commit/5d65ffc24f63de435233003dde660f006e097825))

* tests: Add basic tests for user-mentions and hashtag-extractors ([`3d128d2`](https://github.com/Sieboldianus/lbsntransform/commit/3d128d2fca65dc250b0547cc2e5aeb40efe8629b))

* todo: Add hint to list-append for Twitter mapping ([`e6bccc9`](https://github.com/Sieboldianus/lbsntransform/commit/e6bccc94f267743fe8765fa389fd6826463c15f7))

* deps: Update lbsnstructure dependency to 1.2.0 ([`cde7c49`](https://github.com/Sieboldianus/lbsntransform/commit/cde7c49e08282af91e803455ef84daa53a20b143))

* Merge branch &#39;ci-test&#39; into &#39;master&#39;

Ci test

See merge request lbsn/lbsntransform!15 ([`ba22067`](https://github.com/Sieboldianus/lbsntransform/commit/ba22067cd3b14fb65fbfc64a090424fe043f89a9))

* Merge branch &#39;tests&#39; into &#39;master&#39;

Tests

See merge request lbsn/lbsntransform!14 ([`878ab08`](https://github.com/Sieboldianus/lbsntransform/commit/878ab08e3be70a8224b2afc8ee50b6f8ffbd4c8c))

* tests: Add YFCC integration test and update CI ([`312b958`](https://github.com/Sieboldianus/lbsntransform/commit/312b9587884e773405b8ff6d605af4637e97a25b))

* dev: Pytest testpaths ([`ee564cd`](https://github.com/Sieboldianus/lbsntransform/commit/ee564cdb26dbe8aeb844f87ee766a2f1e3bcab63))

* dev: Add pytest to depdendencies ([`fb21071`](https://github.com/Sieboldianus/lbsntransform/commit/fb21071062306c6a5aed7285ccdd54eaf0e2adbe))

* 0.24.2 ([`b5ed646`](https://github.com/Sieboldianus/lbsntransform/commit/b5ed6466488816f24ee4799884ce93f689d36950))


## v0.24.2 (2023-05-09)

### Chore

* chore: Update black formatting with config.py exclude ([`cc4aa3b`](https://github.com/Sieboldianus/lbsntransform/commit/cc4aa3b69ba3e656bde014ca014f8eb8d21eba92))

### Documentation

* docs: Update to reflect pyproject.toml only based setup ([`6bce8d9`](https://github.com/Sieboldianus/lbsntransform/commit/6bce8d9e4784709ab25d6ea6944edfd89edea880))

* docs: Fix formatting in cli-commands page ([`c482347`](https://github.com/Sieboldianus/lbsntransform/commit/c4823478aa9c7a2574fd06a26e57d6739de17542))

### Fix

* fix: Update yml dependencies to use version range for protobuf, too ([`bfad7b2`](https://github.com/Sieboldianus/lbsntransform/commit/bfad7b26d2537a6855246f02885dd9b592938121))

* fix: Migrate from setup.cfg to pyproject.toml

fixes: #7 ([`7ee7598`](https://github.com/Sieboldianus/lbsntransform/commit/7ee759805566b58f7ec295b5ad2f70fc03a5dfd2))

### Unknown

* Fix pipeline badge URL in README.md ([`ded258e`](https://github.com/Sieboldianus/lbsntransform/commit/ded258e18a279dd29cd4f1fcf955af9fad8f45ef))

* Source path update to version.py ([`825008d`](https://github.com/Sieboldianus/lbsntransform/commit/825008d91653fe68d855b2fffdff16ed91b49765))

* ci - use version from file

ERROR: Job failed: exit code 1 (?) ([`21c4f3c`](https://github.com/Sieboldianus/lbsntransform/commit/21c4f3cd3736c7d4b2ef12f17316160cf57aa2d0))

* Fix argparse indentation error ([`8ba2828`](https://github.com/Sieboldianus/lbsntransform/commit/8ba2828b5b2acedadceae9522189d4fcfd98d17b))

* Cleanup step after semantic-version fix ([`804d464`](https://github.com/Sieboldianus/lbsntransform/commit/804d4645aeedfd7e47defaaafe537ec24fdd27df))


## v0.24.1 (2023-05-05)

### Unknown

* Use tags as singe-point-of-truth for version source ([`62fa9b3`](https://github.com/Sieboldianus/lbsntransform/commit/62fa9b3b79aab9a32b973d4afd53a94f462c4469))


## v0.24.0 (2023-05-05)

### Ci

* ci: Fix semantic-release version flow ([`d4d62a5`](https://github.com/Sieboldianus/lbsntransform/commit/d4d62a531f84a1584e607a30293d236aac0179bd))

* ci: Use version from git tags ([`ef7be73`](https://github.com/Sieboldianus/lbsntransform/commit/ef7be73e15610f5560ff9c512ed36b914cbb4d23))

* ci: Update documentation deployment from external to GL pages ([`34352d9`](https://github.com/Sieboldianus/lbsntransform/commit/34352d9d591fbbb1e8e2036f2cc5fb1273d897f7))

### Documentation

* docs: Add information regarding semantic release versioning ([`eb667d4`](https://github.com/Sieboldianus/lbsntransform/commit/eb667d4d866826ed34bbda174bb4f8f9034e33bb))

* docs: Update installation instructions based on new dependencies and deprecated setup.py ([`416c869`](https://github.com/Sieboldianus/lbsntransform/commit/416c869d41dace88c12f8e6270644f470d02332e))

* docs: Add a short description of the file structure and layout ([`d56041d`](https://github.com/Sieboldianus/lbsntransform/commit/d56041d16c06b6389b67bf3aaad7e98dae43978f))

### Feature

* feat: Migrate from setup.py to pyproject.toml ([`7de0de0`](https://github.com/Sieboldianus/lbsntransform/commit/7de0de0480fb1b9956de5cc0c34c52536627b892))

### Refactor

* refactor: Update mappings to match new lbsnstructure spec ([`701f2eb`](https://github.com/Sieboldianus/lbsntransform/commit/701f2ebaaafd92a231842098de8cd123f3e72846))

* refactor: Follow the standard src-layout for setuptools ([`0e6d96a`](https://github.com/Sieboldianus/lbsntransform/commit/0e6d96a9fa7670de7961027379c589c3058c82f4))

### Unknown

* Working merge for file-based semantic versioning using setup.cfg and pyproject.toml ([`3d1b724`](https://github.com/Sieboldianus/lbsntransform/commit/3d1b724b0798dcb3bca5e0e1674c42bff397ebff))

* Fix build ([`e095227`](https://github.com/Sieboldianus/lbsntransform/commit/e095227c970b525163781e2ba3179d9596f1c2bf))

* dependencies: Pin lbsnstructure&gt;=1.0.3 with protobuf 4.19.0 compiled ([`fc99f2e`](https://github.com/Sieboldianus/lbsntransform/commit/fc99f2e0c37f425222c2cfe0f2e27c4e1e7029da))

* dependencies: Pin shapely&lt;2.0.0 until GEOS.WKTWriter is available ([`847ab81`](https://github.com/Sieboldianus/lbsntransform/commit/847ab81e54c236fafb560c9e19041c7528ecbc6b))

* Fix docs wrong folder ([`de3515a`](https://github.com/Sieboldianus/lbsntransform/commit/de3515a484edd18a87a39af2f8210249fbb30d46))

* Fix paths in ci ([`4858388`](https://github.com/Sieboldianus/lbsntransform/commit/48583882917617ff52b8b23f175d04a585a26a4e))

* Fix paths ([`a7e2d7d`](https://github.com/Sieboldianus/lbsntransform/commit/a7e2d7d2a690a8cbf9930fa81ee24bc798bab42e))

* Fix cp: can&#39;t create &#39;public/...&#39; ([`18271f3`](https://github.com/Sieboldianus/lbsntransform/commit/18271f34d2844086ac308851ecbf90f26441a106))

* Fix paths in documentation deploy ([`cbae069`](https://github.com/Sieboldianus/lbsntransform/commit/cbae0690d08b4b84aeb82406904c6909c3c92df2))


## v0.23.0 (2022-11-24)

### Chore

* chore: Also update pinning of protobuf in setup.py ([`1bc1974`](https://github.com/Sieboldianus/lbsntransform/commit/1bc19749a7627766692326932c8c48446785ff99))

* chore: Update dependency pinnings and dev environment ([`aaf70f5`](https://github.com/Sieboldianus/lbsntransform/commit/aaf70f5dc3258380c2587990b860556849ed9a5a))

* chore: Pin emoji package to &gt;=2.0.0 ([`fa8a129`](https://github.com/Sieboldianus/lbsntransform/commit/fa8a1296a85a47ba84841b2e8e7a094581f6fad5))

### Documentation

* docs: Fix typo ([`7e43ef4`](https://github.com/Sieboldianus/lbsntransform/commit/7e43ef43bbca4ec4452d04ce7afcff44149fab52))

* docs: Fix typo in --commit_volume cli docs ([`70d96b9`](https://github.com/Sieboldianus/lbsntransform/commit/70d96b90a6a5df5cfff5c2e73375b5a1e490f78a))

### Feature

* feat: Add experimental temporal._month_hashtag_latlng base processing ([`60da223`](https://github.com/Sieboldianus/lbsntransform/commit/60da223bdaa56f714b4d6fb8889ad879183790b9))

### Fix

* fix: NLTK stopwords not available notice ([`c395bcb`](https://github.com/Sieboldianus/lbsntransform/commit/c395bcb1404cc135a85f1e65efd29af57efed4d2))

* fix: EMOJI_UNICODE deprecated in emoji&gt;=2.0.0

Use the official function to extract distinct unicode emoji from string, available from emoji 2.0.0 on ([`3097a42`](https://github.com/Sieboldianus/lbsntransform/commit/3097a42df36e245234562582c97b6b93f655cccd))

* fix: Typo ([`05c623c`](https://github.com/Sieboldianus/lbsntransform/commit/05c623c213faee91dc0771e823b00166ba8d1a6b))

### Unknown

* Merge branch &#39;composite-feature-multi&#39; into &#39;master&#39;

Composite feature multi base

See merge request lbsn/lbsntransform!13 ([`a612b4e`](https://github.com/Sieboldianus/lbsntransform/commit/a612b4e0effef846bf96df085c53e5172542ef50))

* Update CHANGELOG.md ([`990ca8f`](https://github.com/Sieboldianus/lbsntransform/commit/990ca8f08bb62b257d0e36ecaff96a18a116c3a4))

* Merge branch &#39;master_gh&#39; into master_new ([`1ea3d66`](https://github.com/Sieboldianus/lbsntransform/commit/1ea3d666577cce1b4ad76f985f1e97815f67889e))

* Fix typo ([`a995b6f`](https://github.com/Sieboldianus/lbsntransform/commit/a995b6f1bd6685667741f7bc4675ff52f1702aa5))

* Update setup.py

Fix: Vulnerability in protobuf dependency ([`dcf7a45`](https://github.com/Sieboldianus/lbsntransform/commit/dcf7a450dc8ea2a9ed67791a9e6a0be9dc3ff1ae))

* Fix typo ([`bd70415`](https://github.com/Sieboldianus/lbsntransform/commit/bd70415a17807c71c5f48168c9bcb78785bdcbc3))

* Fix emoji extract missing commits ([`25e49e1`](https://github.com/Sieboldianus/lbsntransform/commit/25e49e1f74303d0d21aea597a30fb58cf946dcaf))


## v0.22.1 (2022-11-23)

### Chore

* chore: Update dependency pinnings and dev environment ([`4717c7a`](https://github.com/Sieboldianus/lbsntransform/commit/4717c7a8489563a26677b7d0d72dc5a4d50459bc))

* chore: Pin emoji package to &gt;=2.0.0 ([`f4a39ec`](https://github.com/Sieboldianus/lbsntransform/commit/f4a39ec3863edc3cc33316e7c26a50ef48390f9b))

* chore: Add instagram mapping example ([`985ee26`](https://github.com/Sieboldianus/lbsntransform/commit/985ee26ff23160927d425c7a9a0c0f1f481db5bc))

### Documentation

* docs: Fix typo ([`63ba7e4`](https://github.com/Sieboldianus/lbsntransform/commit/63ba7e4eac6902777cedcd605496e7e91d0b60ab))

* docs: Fix typo in --commit_volume cli docs ([`c36d9aa`](https://github.com/Sieboldianus/lbsntransform/commit/c36d9aab72738859906af73a925cb6ee05f19ad7))

* docs: Better explain the use of ([`e43afdd`](https://github.com/Sieboldianus/lbsntransform/commit/e43afdd8e359143cdb58cad3c5d00019cf237fa9))

* docs: Clarify to use all lbsn objects by default when mapping from lbsn raw ([`202fd75`](https://github.com/Sieboldianus/lbsntransform/commit/202fd759e9127d2761ff189623b5c8d9d9ad8c6e))

* docs: Fix internal link ([`67f4c90`](https://github.com/Sieboldianus/lbsntransform/commit/67f4c90ab77e780b60018483a8ec9891fd08cab0))

* docs: Improve description of --include_lbsn_bases and --commit_volume args ([`b7697a3`](https://github.com/Sieboldianus/lbsntransform/commit/b7697a315c01eb09513cc75048fc5151cdfed91f))

* docs: Add header information on command line interface page ([`9602c47`](https://github.com/Sieboldianus/lbsntransform/commit/9602c47dad3eddb5b32941619d124e794406be6b))

* docs: Add changelog to documentation ([`766a40d`](https://github.com/Sieboldianus/lbsntransform/commit/766a40d8335f7d7f32fa801f4b8ef75d43e6401c))

### Fix

* fix: EMOJI_UNICODE deprecated in emoji&gt;=2.0.0

Use the official function to extract distinct unicode emoji from string, available from emoji 2.0.0 on ([`599158a`](https://github.com/Sieboldianus/lbsntransform/commit/599158abf4126981314472878662cfb2d773ba01))

* fix: Typo ([`5145455`](https://github.com/Sieboldianus/lbsntransform/commit/51454555c9f6ed51e8a56ff76c1d6ac2a8dcd90b))

* fix: --skip_until_file not implemented ([`18e7665`](https://github.com/Sieboldianus/lbsntransform/commit/18e7665fed14a027889e93f59f4e022702a86500))

* fix: Fix TypeError NoneType for skipped_geo reporting ([`fe67231`](https://github.com/Sieboldianus/lbsntransform/commit/fe6723137a7ac6c1170acea55c1353698058d3b0))

* fix: Catch empty values in lbsn database record arrays ([`6ad2d82`](https://github.com/Sieboldianus/lbsntransform/commit/6ad2d82876e75533d8fd3ec072e03775311383e0))

### Performance

* perf: Clear key hashes on finalize_output() ([`864336d`](https://github.com/Sieboldianus/lbsntransform/commit/864336deee218c48602d17a20586ad285e300482))

### Refactor

* refactor: Add docstring and remove remnant ([`36a4f2d`](https://github.com/Sieboldianus/lbsntransform/commit/36a4f2d95d926336d9a82f0796a4c16cea3b5d1f))

* refactor: Same indent for all doctsrings in argparse ([`8fa91fb`](https://github.com/Sieboldianus/lbsntransform/commit/8fa91fb18955d2fd1d280f169b4948901fb664bc))

### Style

* style: Fix indent ([`d617e00`](https://github.com/Sieboldianus/lbsntransform/commit/d617e0073ca0fcecf042e6f19afbf6ddc2807921))

* style: Fix docs formatting ([`43ddea3`](https://github.com/Sieboldianus/lbsntransform/commit/43ddea35b0f4736539e184afbe46af37a29e090f))

### Unknown

* Fix emoji extract missing commits ([`1c309a3`](https://github.com/Sieboldianus/lbsntransform/commit/1c309a368124844a3db3e9eaae6fa9f1d1e726fd))

* Merge branch &#39;fix-emoji-extract&#39; into &#39;master&#39;

fix: EMOJI_UNICODE deprecated in emoji&gt;=2.0.0

See merge request lbsn/lbsntransform!12 ([`12e0d0f`](https://github.com/Sieboldianus/lbsntransform/commit/12e0d0f1f6528e95356c8c3f77f6e389b2cb560b))

* Update setup.py

Fix: Vulnerability in protobuf dependency ([`dbf224e`](https://github.com/Sieboldianus/lbsntransform/commit/dbf224e5abb7d1fa1925a17551d00c8d5c450df7))

* Minor clarification ([`9e50f27`](https://github.com/Sieboldianus/lbsntransform/commit/9e50f274f53c8e736bf1dbd736b3a06ce31f554b))

* Fix minor typo ([`94ec55a`](https://github.com/Sieboldianus/lbsntransform/commit/94ec55a1c6eff23f5f1865d7064561ccea614f8c))

* Fix typo in docstring ([`c4d4b64`](https://github.com/Sieboldianus/lbsntransform/commit/c4d4b64a6da0c32e10552279f4b609dd08082701))

* Fix loop for dictionary values ([`5946db2`](https://github.com/Sieboldianus/lbsntransform/commit/5946db23eef368df3fd528c68af85e6d1bad950c))

* Fix: Typo ([`6d24ff0`](https://github.com/Sieboldianus/lbsntransform/commit/6d24ff07d8d69091865a56c4d60b4028a2edfcbb))

* Fix argparse argdown for cli documentation ([`f0b91da`](https://github.com/Sieboldianus/lbsntransform/commit/f0b91dab73ad6c16456cc83c6264135455b254af))


## v0.22.0 (2022-04-08)

### Documentation

* docs: Fix typo ([`4034867`](https://github.com/Sieboldianus/lbsntransform/commit/4034867ef09d357b730b00b8ea2db84abbad4a17))

* docs: Add internal links to Use Cases ([`da93d5c`](https://github.com/Sieboldianus/lbsntransform/commit/da93d5c053b94a16a76803abde486e36e95d15fa))

* docs: Add twitterparser example to use lbsntransform as a package ([`2a68f08`](https://github.com/Sieboldianus/lbsntransform/commit/2a68f086ebfdf8d64d15e6072b4c1a66249539c4))

### Feature

* feat: Allow --commit_volume to be overriden

To prevent deadlocks on concurrent lbsntransform writes (e.g. multiple processes running at the same time ([`50c4bf8`](https://github.com/Sieboldianus/lbsntransform/commit/50c4bf849dc453ccad778f5735a19c8a00d068cf))

### Fix

* fix: Skip all base records with any empty key

Primary Key constraints automatically add NOT NULL constraint in postgres, thus empty keys are not allowed and can cause errors on incomping records, where information is missing (e.g. empty post_create_date for &#39;date&#39; base) ([`e3caac1`](https://github.com/Sieboldianus/lbsntransform/commit/e3caac1437a4c1ef95ef14ad2be5488eb9c438b2))

* fix: Skip empty keys for temporal hll structures ([`263774c`](https://github.com/Sieboldianus/lbsntransform/commit/263774c3f815b2bc66dc54e8f8d780400eb512f3))

* fix: Compatibility for &#39;carousel&#39; types from previous lbsnstructure ([`caf21c3`](https://github.com/Sieboldianus/lbsntransform/commit/caf21c3af7882beb70525008a016ccb563dd4357))


## v0.21.3 (2022-03-18)

### Documentation

* docs: Add note to activate optional nltk stopwords filter feature ([`015511e`](https://github.com/Sieboldianus/lbsntransform/commit/015511e27863b1b2f63176c498fc8b85f2721707))

* docs: Deprecate cx_freeze setup ([`4700821`](https://github.com/Sieboldianus/lbsntransform/commit/4700821a3e4ca1d107e66fc2cc78b5a2e1ce4ea7))

### Fix

* fix: Pin google.protobuf to latest release 3.19.4 or earlier ([`f591487`](https://github.com/Sieboldianus/lbsntransform/commit/f591487a8d4c3fb71040a26caba2267049f1b657))

### Unknown

* --amend ([`8d810c6`](https://github.com/Sieboldianus/lbsntransform/commit/8d810c657953f00c8663b5d23243304aa9725dda))

* ScalarMapContainer not found in protobuf dependency (Windows only) ([`db98ae7`](https://github.com/Sieboldianus/lbsntransform/commit/db98ae7d27eb3c5ea0f613f590906f1f734623ac))


## v0.21.2 (2022-03-18)

### Documentation

* docs: Add hint towards Linux installation ([`ce2c75b`](https://github.com/Sieboldianus/lbsntransform/commit/ce2c75b68912a2485ae2ef195a7e4bd8dc4137d8))

### Unknown

* Revert &#34;fix: ScalarMapContainer not found in protobuf dependency (Windows only)&#34;

This reverts commit 7d469f5fa2e2ec93a0f02d5ae0c08384cf5c3ec0. ([`f847758`](https://github.com/Sieboldianus/lbsntransform/commit/f847758016cacc724c78738e8c816d1b9943aa63))


## v0.21.1 (2022-03-17)

### Ci

* ci: Fix argdown doc generator ([`f40b3d3`](https://github.com/Sieboldianus/lbsntransform/commit/f40b3d3c80ce52a36bc4436311f4da6d2eca3228))

### Fix

* fix: ScalarMapContainer not found in protobuf dependency (Windows only) ([`7d469f5`](https://github.com/Sieboldianus/lbsntransform/commit/7d469f5fa2e2ec93a0f02d5ae0c08384cf5c3ec0))

* fix: Deactivate currently not supported CSV output ([`92f887d`](https://github.com/Sieboldianus/lbsntransform/commit/92f887d2691e32efe0378471f81862a0f6877c5d))

### Unknown

* Merge branch &#39;fix-composite-container&#39; into &#39;master&#39;

Fix composite container

See merge request lbsn/lbsntransform!11 ([`63351b7`](https://github.com/Sieboldianus/lbsntransform/commit/63351b7807431a8e7fdc68cf9b4cdb3c13e3a1f3))

* Merge branch &#39;ci-test&#39; into &#39;master&#39;

ci: Fix argdown doc generator

See merge request lbsn/lbsntransform!10 ([`a30a068`](https://github.com/Sieboldianus/lbsntransform/commit/a30a068c831d26b1f71395a0f9f03cc38241eea8))


## v0.21.0 (2022-03-15)

### Chore

* chore: Force update badges ([`7779255`](https://github.com/Sieboldianus/lbsntransform/commit/7779255e10409f40539b5c89b1911e7edb19f733))

### Documentation

* docs: Remove duplicate mappings_path from example ([`854aad5`](https://github.com/Sieboldianus/lbsntransform/commit/854aad5df685b71d7a72555e77231c545f2f608a))

* docs: Fix internal links in Use Cases ([`61f772a`](https://github.com/Sieboldianus/lbsntransform/commit/61f772aef4f9dbe837c9d99906bbc004d242bf1a))

### Feature

* feat: Allow lbsntransform args to be predefined by another package ([`c587bbf`](https://github.com/Sieboldianus/lbsntransform/commit/c587bbf3f0f85abcf55e5b193ba947ad204d0914))

### Unknown

* Merge branch &#39;feat-predefined-args&#39; into &#39;master&#39;

feat: Allow lbsntransform args to be predefined by another package

See merge request lbsn/lbsntransform!9 ([`6a770f1`](https://github.com/Sieboldianus/lbsntransform/commit/6a770f1f083baf8077590069d6bae5707de60e00))


## v0.20.0 (2021-05-11)

### Refactor

* refactor: Reflect hlldb design decision to rename date_hll to pud_hll (Picture or Post User Days) ([`4f6d578`](https://github.com/Sieboldianus/lbsntransform/commit/4f6d578232e88282eca2512550d107323cba8774))


## v0.19.0 (2021-05-11)

### Feature

* feat: Add _month_latlng and _month_hashtag composite bases ([`71bbc22`](https://github.com/Sieboldianus/lbsntransform/commit/71bbc222924866a956964326a503ad2408aa3c0a))


## v0.18.3 (2021-05-05)

### Chore

* chore: Fix code block display issue in docs ([`13b2efc`](https://github.com/Sieboldianus/lbsntransform/commit/13b2efcc6353a575f6b6b6e0b5c6a6ea9f740a3e))

* chore: Fix argparse script ([`f8d48ff`](https://github.com/Sieboldianus/lbsntransform/commit/f8d48ff3238f8d4fc6f815a02a62f2f73c0ea5aa))

### Fix

* fix: csv.reader bug that got introduced in #2a79f01c ([`49243c5`](https://github.com/Sieboldianus/lbsntransform/commit/49243c5d663a76d6c8abcc550f113b09cd909bd0))


## v0.18.2 (2021-04-26)

### Documentation

* docs: Improve description on how hmac defaults are used ([`aa5e265`](https://github.com/Sieboldianus/lbsntransform/commit/aa5e2651376efbfc3c9b74504f984b4fd6e75cd8))

### Fix

* fix: On empty hmac, do not override if crypt.salt is set in hll worker db ([`24f0a4d`](https://github.com/Sieboldianus/lbsntransform/commit/24f0a4d535087697e70fe6bd535f77b9e1fb39bb))

### Unknown

* Merge branch &#39;master&#39; of github.com:Sieboldianus/lbsntransform ([`ff79126`](https://github.com/Sieboldianus/lbsntransform/commit/ff79126a858bcad098dcd47019dbc1252fb05bab))


## v0.18.1 (2021-04-19)

### Documentation

* docs: Fix badge links not updating on GH

According to [#1065](https://github.com/lemurheavy/coveralls-public/issues/1065#issuecomment-435494495) ([`8a425ed`](https://github.com/Sieboldianus/lbsntransform/commit/8a425ed986d489791374c7db6e58152a5a31f007))

### Fix

* fix: Error on empty HMAC ([`8d29832`](https://github.com/Sieboldianus/lbsntransform/commit/8d2983204d2496e979c71b39655b66bd512c3d4b))

* fix: Grapheme clusters not found in newest emoji.UNICODE_EMOJI (emoji &gt;= v.1.0.1) ([`cfd6f28`](https://github.com/Sieboldianus/lbsntransform/commit/cfd6f28684c6c56d4a54113fa712f285810289e5))

### Unknown

* Merge branch &#39;master&#39; of github.com:Sieboldianus/lbsntransform ([`994e5ad`](https://github.com/Sieboldianus/lbsntransform/commit/994e5ad7d04ffa184ab7393214f3b81e33e8a45e))


## v0.18.0 (2021-04-16)

### Documentation

* docs: Improve description of --transfer_count ([`9847f5e`](https://github.com/Sieboldianus/lbsntransform/commit/9847f5e485e36bcab7ff56261277a514573be01c))

* docs: Fix docstring typo ([`7d13423`](https://github.com/Sieboldianus/lbsntransform/commit/7d13423877622306fe39208de1d0b518b9538a77))

### Feature

* feat: Add function to extract @-Mentions from string ([`714d5c9`](https://github.com/Sieboldianus/lbsntransform/commit/714d5c9a6b4c1d17805d88232ca8138cd627e18f))

* feat: Add option to switch to csv.DictReader() ([`2a79f01`](https://github.com/Sieboldianus/lbsntransform/commit/2a79f01cf259a7f2d74763d7adbed8dd59f65488))


## v0.17.0 (2021-04-15)

### Documentation

* docs: Fix list formatting ([`2751d74`](https://github.com/Sieboldianus/lbsntransform/commit/2751d742480a60f09d3e90e0387144743678b4eb))

* docs: Fix typo ([`e000386`](https://github.com/Sieboldianus/lbsntransform/commit/e000386a9899b7c8c732282fb54331d8efbaf18b))

* docs: Update Windows install instructions ([`9d0cb6e`](https://github.com/Sieboldianus/lbsntransform/commit/9d0cb6e393452d4e4e637a20fefd0b0ece1c1fea))

* docs: Fix api link ([`b31b1ce`](https://github.com/Sieboldianus/lbsntransform/commit/b31b1ce2997aa45f3b1bebcc0af7312c57e560d1))

* docs: Fix api link ([`1745f39`](https://github.com/Sieboldianus/lbsntransform/commit/1745f3942b737a86af0c9c666754692972431642))

* docs: Add last git revision date to pages ([`b254df7`](https://github.com/Sieboldianus/lbsntransform/commit/b254df7cc4bf0aa029a22c19e050a99a961cca8d))

### Feature

* feat: Properly intergrate hmac hashing and warn user on empty key ([`4cecd96`](https://github.com/Sieboldianus/lbsntransform/commit/4cecd961a79d8e14e047b59eab11ce2498bf02ff))


## v0.16.1 (2021-03-13)

### Chore

* chore: Add Dockerfile and update docs ([`2f9afae`](https://github.com/Sieboldianus/lbsntransform/commit/2f9afaefebd98f58d23d3005d3560e99733998f9))

* chore: fix ci yaml ([`11e8a45`](https://github.com/Sieboldianus/lbsntransform/commit/11e8a4543274c9021c2d4924d7b10c19f9895471))

### Documentation

* docs: Fix Readme image link on pypi ([`ec352ca`](https://github.com/Sieboldianus/lbsntransform/commit/ec352cad0d9ded60b6dc719e6c19cbb6787519de))

* docs: Major overhaul of CLI argument formatting ([`d12b4c1`](https://github.com/Sieboldianus/lbsntransform/commit/d12b4c1056b0fd496ed1c907a51321870f17927b))

* docs: Improve formatting ([`c766d8e`](https://github.com/Sieboldianus/lbsntransform/commit/c766d8ed9a95d1247f26fb55bf97294ae705fbf0))

* docs: Add docker mount note ([`dcd98a2`](https://github.com/Sieboldianus/lbsntransform/commit/dcd98a225df5cb19a6940d63d7916d91464b73ed))

* docs: Add note towards Docker input from bind mounts ([`a1e1564`](https://github.com/Sieboldianus/lbsntransform/commit/a1e156484832945bd30e0544849027bdbd851ef1))

* docs: Fix formatting issue in --override_lbsn_query_schema ([`ac26a2f`](https://github.com/Sieboldianus/lbsntransform/commit/ac26a2fff373261996b2662c47d653d58393ff8b))

* docs: fix typo ([`42fe31f`](https://github.com/Sieboldianus/lbsntransform/commit/42fe31ff43bfb2210a28b6d669678dd2631504ab))

* docs: Add example to read from live lbsn db and to live hll db ([`b07a7c2`](https://github.com/Sieboldianus/lbsntransform/commit/b07a7c2e12e83a7f7398284a90f94fcd31456e1e))

* docs: correct order of --editable --no-deps for quirky pip ([`a768da1`](https://github.com/Sieboldianus/lbsntransform/commit/a768da14edc2b82a916e9e844501456a8cabefdb))

### Refactor

* refactor: Docs structure and formatting ([`1449aca`](https://github.com/Sieboldianus/lbsntransform/commit/1449aca59a21203733ab9b10d86174c28e48d523))

* refactor: CLI arg docstring formatting ([`aedd00c`](https://github.com/Sieboldianus/lbsntransform/commit/aedd00c52fd00d3bd5a932952c3eae9556e328ef))

* refactor: Remove empty default passwords ([`f4f2e15`](https://github.com/Sieboldianus/lbsntransform/commit/f4f2e15efa4a8d3f1777dc9a795162d247a373d6))

* refactor: Use absolute imports instead of relative ([`ab8db19`](https://github.com/Sieboldianus/lbsntransform/commit/ab8db19b5c99fc2b7ebc2a0223bdf8c0c7825903))

### Unknown

* Minor cleanup ([`fbdc69b`](https://github.com/Sieboldianus/lbsntransform/commit/fbdc69b18fa3bd76cde1a249d33233ca44c006f4))

* Restructure markdown formatting ([`7ee2298`](https://github.com/Sieboldianus/lbsntransform/commit/7ee2298ef829536e18f2b43841bec78b3d67ec50))

* Minor formatting fix ([`0cfa7a3`](https://github.com/Sieboldianus/lbsntransform/commit/0cfa7a37413b47823ec742459491cb31a24a09c7))

* Fix code blocks in argument docs ([`ec5d7a0`](https://github.com/Sieboldianus/lbsntransform/commit/ec5d7a0decb1b480596ba9a2e9adff90777eec4f))

* Fix link ([`d1de7e3`](https://github.com/Sieboldianus/lbsntransform/commit/d1de7e39079b7058b099c11b4b076b40f239bf07))

* Fix typo ([`74c6a11`](https://github.com/Sieboldianus/lbsntransform/commit/74c6a11685d80dd12c16fda4ca22b42640611ceb))

* Minor formatting fix ([`ff8cffb`](https://github.com/Sieboldianus/lbsntransform/commit/ff8cffb5888604932e433018424533fd3cb50639))

* Minor formatting fix ([`e6c73fc`](https://github.com/Sieboldianus/lbsntransform/commit/e6c73fc01207d018b00aedef7fa8e2014f802e7c))

* Fix linK ([`e054f01`](https://github.com/Sieboldianus/lbsntransform/commit/e054f01dcbfce23a2152ce944843fd0a8c275539))

* Minor formatting fix ([`a1791ae`](https://github.com/Sieboldianus/lbsntransform/commit/a1791aec94abfd23334a7e4d7aef9778a52521f7))

* Minor formatting fix ([`fcdac9a`](https://github.com/Sieboldianus/lbsntransform/commit/fcdac9aa68d7461d8f8b35fa0186f4df9d536ea9))

* Minor formatting fix ([`61f286f`](https://github.com/Sieboldianus/lbsntransform/commit/61f286fa8a6cc4241ed6d71edb92833b3b40cf44))

* Merge branch &#39;dev&#39; ([`9481e09`](https://github.com/Sieboldianus/lbsntransform/commit/9481e09d55e34c8aaae091467548f45a4ce0133e))

* Improve docs format of headings ([`eaabc88`](https://github.com/Sieboldianus/lbsntransform/commit/eaabc88bb3104015670575bdb8a3f6b8be8f233b))

* Fix markdown formatting ([`22aac5c`](https://github.com/Sieboldianus/lbsntransform/commit/22aac5c0561ef66a46bf946ee33bad3451374622))

* Minor formatting ([`9bd065b`](https://github.com/Sieboldianus/lbsntransform/commit/9bd065b9184d01215eb30d5273cce0637569ed76))

* Fix csv not available for syntax highlight ([`59eb48b`](https://github.com/Sieboldianus/lbsntransform/commit/59eb48b5cc1f488b9b8add6e48457f03d369371d))

* Merge branch &#39;dev&#39; ([`7ff450e`](https://github.com/Sieboldianus/lbsntransform/commit/7ff450ea2140863516c6bf234f0ae31a14d2026a))

* Merge branch &#39;master&#39; of gitlab.vgiscience.de:lbsn/lbsntransform ([`2f312ea`](https://github.com/Sieboldianus/lbsntransform/commit/2f312eab42802d4a3edf76dab5e0985bdea77499))

* Merge branch &#39;re-master&#39; into &#39;master&#39;

it works

See merge request lbsn/lbsntransform!8 ([`5f9ec06`](https://github.com/Sieboldianus/lbsntransform/commit/5f9ec0641977ce170d8140c4b616f1c9bd7fec7e))

* it works ([`78e784e`](https://github.com/Sieboldianus/lbsntransform/commit/78e784e282981832f83a2e0f5788ce47452094cb))

* Merge branch &#39;docker-image&#39; into &#39;master&#39;

chore: fix ci yaml

See merge request lbsn/lbsntransform!7 ([`3ff4150`](https://github.com/Sieboldianus/lbsntransform/commit/3ff41509bb7619192f272d2ab691748a6b17db9b))

* Merge branch &#39;docker-image&#39; into &#39;master&#39;

build a docker image and push it into the registry

See merge request lbsn/lbsntransform!6 ([`64668ed`](https://github.com/Sieboldianus/lbsntransform/commit/64668ed1214944cc81ea92bc0c1cf2571a41af50))

* push without tag, when on master ([`c5532aa`](https://github.com/Sieboldianus/lbsntransform/commit/c5532aad19f69ea6382241e49cf66b638181374c))

* multi-stage ([`85c270b`](https://github.com/Sieboldianus/lbsntransform/commit/85c270b93e9f39c5de5d13c486b47e121828e4cc))

* 270MB ([`065b9f9`](https://github.com/Sieboldianus/lbsntransform/commit/065b9f946b0e772c16aa1bd5793ad25d9650ace3))

* build-essential 476MB ([`3d6ca5a`](https://github.com/Sieboldianus/lbsntransform/commit/3d6ca5a2947e32670763196f5b718f5a6fcd1e8f))

* build-essential 494MB ([`00751d2`](https://github.com/Sieboldianus/lbsntransform/commit/00751d2da2e6780ec3b481e6af75f718f013932d))

* build a docker image and push it into the registry ([`eb6fb27`](https://github.com/Sieboldianus/lbsntransform/commit/eb6fb27b587fe80687d4d48dd0f5ef1f42635eb8))

* Minor update to docstring ([`470e1bc`](https://github.com/Sieboldianus/lbsntransform/commit/470e1bc6b5ade17af9798b526433d45fe08925a9))


## v0.16.0 (2021-01-14)

### Chore

* chore: Get version from version.py ([`bb201b4`](https://github.com/Sieboldianus/lbsntransform/commit/bb201b493616da6c5de4fff19180f9c794d67952))

### Documentation

* docs: Update linux install command ([`bc35783`](https://github.com/Sieboldianus/lbsntransform/commit/bc35783d7d9c352dd4c83a5acd1220533c9d9325))

* docs: Update and cleanup Readme ([`f16cf2c`](https://github.com/Sieboldianus/lbsntransform/commit/f16cf2c15fc5d841e47fa80308d5d360d4aa11c0))

* docs: Re-order recommended pip setup instructions ([`19e4575`](https://github.com/Sieboldianus/lbsntransform/commit/19e45759233d6b2ffc788d21e879bcf47f768358))

### Feature

* feat: Add --dry-run option ([`335631b`](https://github.com/Sieboldianus/lbsntransform/commit/335631b0b2a49eb18a9e25c852a6cca70d8ea9b1))

### Fix

* fix: Disable CSV output until further notice ([`2014ce5`](https://github.com/Sieboldianus/lbsntransform/commit/2014ce5ac5e18aadb2bacdde62b7b6e954b217b9))

### Unknown

* Remove executable bit ([`36a4b50`](https://github.com/Sieboldianus/lbsntransform/commit/36a4b507d06ab79e5b03c0c85a88ebdb6af94ce9))

* Minor typo ([`e7c2658`](https://github.com/Sieboldianus/lbsntransform/commit/e7c26582e1c5545acbe9cbc51f6f38e9a9b84652))

* Minor typo ([`63a01b4`](https://github.com/Sieboldianus/lbsntransform/commit/63a01b4cdfef3528bac8a235014745adbc773772))

* Merge branch &#39;dev&#39; ([`d884ed1`](https://github.com/Sieboldianus/lbsntransform/commit/d884ed13fe9a1cac2792f6c28712445436396c60))


## v0.15.0 (2021-01-09)

### Feature

* feat: add method for hashtag extraction from string ([`134119c`](https://github.com/Sieboldianus/lbsntransform/commit/134119c2c774ea5b952bea2c52d8d49b5bd425f4))

### Fix

* fix: improved exception reporting for malformed records ([`b7b83e2`](https://github.com/Sieboldianus/lbsntransform/commit/b7b83e2bfb96aa179ba791186623aaaf75b026db))

### Style

* style: minor formatting ([`6adfa2b`](https://github.com/Sieboldianus/lbsntransform/commit/6adfa2b9d836b82a3b0f44f88376011523303d99))

### Unknown

* Revert &#34;fix: Catch any geos.WKTReader() exceptions&#34;

This reverts commit 14f7721902cd8a42304f6a80ff6e8d53263684a1. ([`b8cdb99`](https://github.com/Sieboldianus/lbsntransform/commit/b8cdb990bf3792505765f09be01c2f7bc1aad681))

* Merge master ([`1a80f73`](https://github.com/Sieboldianus/lbsntransform/commit/1a80f734030f689e23f98ca90f73eba708c7ba6b))

* --amend ([`f8c6ed4`](https://github.com/Sieboldianus/lbsntransform/commit/f8c6ed4e608e767167e353ecda9ad9e86be15211))


## v0.14.1 (2021-01-06)

### Ci

* ci: Remove pypi search during version badge generation ([`06d90ad`](https://github.com/Sieboldianus/lbsntransform/commit/06d90ad0f959b6ab2a62d3bb17c8f65e6c5a6126))

### Documentation

* docs: Fix admonition formatting ([`c33b8c1`](https://github.com/Sieboldianus/lbsntransform/commit/c33b8c19569c6916ec17c603d7ac423e2301780d))

* docs: update conda install instructions ([`4f0f96b`](https://github.com/Sieboldianus/lbsntransform/commit/4f0f96b421efa606a1c02f86be9243d32093df8a))

* docs: fix links and rehrase sections ([`76875bf`](https://github.com/Sieboldianus/lbsntransform/commit/76875bf497c97fc154facb692e954dbe2e5f16ef))

### Fix

* fix: Catch any geos.WKTReader() exceptions ([`14f7721`](https://github.com/Sieboldianus/lbsntransform/commit/14f7721902cd8a42304f6a80ff6e8d53263684a1))

* fix: Windows lbsntransform.tools module not found. ([`1643112`](https://github.com/Sieboldianus/lbsntransform/commit/1643112ae7662274a408bf873754e58b14273395))

### Unknown

* Formatting fix ([`3a19711`](https://github.com/Sieboldianus/lbsntransform/commit/3a197111f8252d3d88fb81787849b99deea82b38))

* Formatting fix ([`0565450`](https://github.com/Sieboldianus/lbsntransform/commit/0565450ad78f1c039c63a65c81abcaa1eb9118b6))

* Minor typos ([`85df870`](https://github.com/Sieboldianus/lbsntransform/commit/85df8700b3e2a7e8df78b17246cce0fcd5e046ad))

* Fix link to resources ([`aea4741`](https://github.com/Sieboldianus/lbsntransform/commit/aea47419add41dccd80b0c4fd15c1bbf75ee6c92))

* Fix relative links ([`33851fe`](https://github.com/Sieboldianus/lbsntransform/commit/33851fe61aeba83c7cbc9c498a7d8c119cafd66f))

* Minor typos ([`3b08e17`](https://github.com/Sieboldianus/lbsntransform/commit/3b08e17f10530383bc5fcdcb99e072d62b68c865))

* Fix relative links in docs ([`985236a`](https://github.com/Sieboldianus/lbsntransform/commit/985236acda9eebdb0e67a98b1a4ef46b6a135a8f))


## v0.14.0 (2020-12-11)

### Documentation

* docs: Fix linebreak conversion on python to markdown arg-docstring conversion ([`ec14cc0`](https://github.com/Sieboldianus/lbsntransform/commit/ec14cc046417f4cf31e9c534fa28e82bf07b0990))

### Feature

* feat: Dynamic load of mapping modules

Remove obsolete mapping modules

Minor refactor mapping load

fix yml formatting errors

Minor formatting in docs ([`4168509`](https://github.com/Sieboldianus/lbsntransform/commit/4168509960839dc39b3030b95b233a23c6163814))

* feat: Dynamic load of mapping modules ([`09de72f`](https://github.com/Sieboldianus/lbsntransform/commit/09de72f23b5465e5928267d118c132607f5c9a74))

### Unknown

* Minor formatting in docs ([`e719714`](https://github.com/Sieboldianus/lbsntransform/commit/e71971436f4a83c65c2e7eaa3c3c48761b670a03))

* fix yml formatting errors ([`1d3831c`](https://github.com/Sieboldianus/lbsntransform/commit/1d3831c4d1109d39b8ace1559d03b9ec8e80f0fe))

* Minor refactor mapping load ([`108b97d`](https://github.com/Sieboldianus/lbsntransform/commit/108b97d333e721552c275db493f7ddbb528a731a))

* Remove obsolete mapping modules ([`93d7759`](https://github.com/Sieboldianus/lbsntransform/commit/93d7759c076e9cfd96858d9b035624f841e4c87c))

* Move example mappings to resources folder ([`91f31f1`](https://github.com/Sieboldianus/lbsntransform/commit/91f31f167efe866cf23030346e5ab1781353ebb1))

* Update docs with more examples ([`5b32cb2`](https://github.com/Sieboldianus/lbsntransform/commit/5b32cb2f2c6af1fc18ea0856a966d23c402f0cbd))

* Compatibility for 1.4.0 LBSN protobuf structure version ([`51af268`](https://github.com/Sieboldianus/lbsntransform/commit/51af2685301078e33d3549a046abbbf7ba2ea2b7))

* Add python and bash to highlightjs config of mkdocs ([`902127c`](https://github.com/Sieboldianus/lbsntransform/commit/902127ca92def4f4b5cbee152a9884c354d7109e))

* Update links in docs ([`0897bdd`](https://github.com/Sieboldianus/lbsntransform/commit/0897bddfa7d91be56b1db551f7d3278e8fa2d2fa))

* fixup: invalid linebreak after markdown link format in docs ([`59184dc`](https://github.com/Sieboldianus/lbsntransform/commit/59184dc492d4196910603e817ac9b42537da0d45))

* fixup: invalid linebreak after markdown link format in docs ([`632a8e7`](https://github.com/Sieboldianus/lbsntransform/commit/632a8e7dfd1d546907dc9957560321438f74c6ce))

* fixup: additional linebreak after colon in markdown lists ([`f0e4da2`](https://github.com/Sieboldianus/lbsntransform/commit/f0e4da271d36269562ee60da0fd9efe9bd519481))

* fixup: use space character in *.md file ([`44fa92e`](https://github.com/Sieboldianus/lbsntransform/commit/44fa92eed6c15235088200fb7ba48dace67fd0ef))

* Merge branch &#39;dev&#39; ([`ed27a32`](https://github.com/Sieboldianus/lbsntransform/commit/ed27a32c2a3f6c0efa8e9cb8b73198cb12d05aa7))

* Add a quite recognizable hint to the docs. ([`48a85d5`](https://github.com/Sieboldianus/lbsntransform/commit/48a85d59ea72960f476d51c293d6384cd3bf2dca))


## v0.13.0 (2020-05-12)

### Chore

* chore: MANIFEST.in recursive-include of submodules ([`80d4f65`](https://github.com/Sieboldianus/lbsntransform/commit/80d4f65edbe3d9b96a1128d8936cb5ea8abf4ac2))

* chore: update manifest, clean setup.py ([`2b74ef3`](https://github.com/Sieboldianus/lbsntransform/commit/2b74ef3142823e4d48fa77fee1a0c83f508e54a2))

### Ci

* ci: fix missing stopwords in pdoc3 doc generation ([`606ab7f`](https://github.com/Sieboldianus/lbsntransform/commit/606ab7f6da57083981f4f59637128dd74d798ea7))

* ci: transition from gitlab only syntax to new if syntax ([`fd9c011`](https://github.com/Sieboldianus/lbsntransform/commit/fd9c011cb00be9d1e4de6a69a3f37d4532ef61e0))

### Documentation

* docs: add submodule docstrings ([`ed9b754`](https://github.com/Sieboldianus/lbsntransform/commit/ed9b754b18ab60263598e7b35f5d0d5f78c90545))

* docs: include __main__ in api-docs, exclude empty submodule inits ([`a1d3e00`](https://github.com/Sieboldianus/lbsntransform/commit/a1d3e0086b7fd67f6843eea580f84080a1db426a))

* docs: Update installation instructions ([`0a90472`](https://github.com/Sieboldianus/lbsntransform/commit/0a9047297f324e5209cbd06f82dc2ec2734a1d91))

* docs: Add instructions for using conda package manager ([`bd58d2b`](https://github.com/Sieboldianus/lbsntransform/commit/bd58d2b819e6bdc16e0b2345e50a42bf8213d96f))

### Feature

* feat: add topical._hashtag_latlng and social.community base ([`d20e766`](https://github.com/Sieboldianus/lbsntransform/commit/d20e766deea7b0310f57a75850abd3ca83f7910d))

* feat: optional schema name override in cli ([`7c05673`](https://github.com/Sieboldianus/lbsntransform/commit/7c05673bb382e2277db620a8d0d5be51e1d01d62))

### Fix

* fix: emoji extracted from body do not include grapheme clusters ([`1ddf046`](https://github.com/Sieboldianus/lbsntransform/commit/1ddf046df7a3ca30ebad7e9a3c3075885084b7f4))

* fix: correct measure of userdays (hll) ([`36d6fa2`](https://github.com/Sieboldianus/lbsntransform/commit/36d6fa2b37fc2fcf1cfc3e9d0ae14f69fbdbea6d))

### Refactor

* refactor: rename module input_data to input ([`0635767`](https://github.com/Sieboldianus/lbsntransform/commit/0635767f8cc278423f384cabce1999408f9fcbad))

### Unknown

* Update pdoc format to process submodules ([`75dd5d9`](https://github.com/Sieboldianus/lbsntransform/commit/75dd5d96f31b5bb84bbb2113591fba0967dfba2c))

* Update Flickr YFCC place match ([`4e17002`](https://github.com/Sieboldianus/lbsntransform/commit/4e1700295d885c5b11a16470cc7f259cf80b3140))

* Use sane_lists extensioN ([`eb022fa`](https://github.com/Sieboldianus/lbsntransform/commit/eb022fa7f409908aed0bfb59b64c982a486a5d40))

* Use highlightjs for fenced code blocks ([`adf0180`](https://github.com/Sieboldianus/lbsntransform/commit/adf018093240434fa5d8eecbd545f69148683349))

* Explicitly highlight code-blocks in config ([`b5fb5ca`](https://github.com/Sieboldianus/lbsntransform/commit/b5fb5ca84bb372e8d26eb6c0cc923c3f8790a402))

* Fix site_url parameter for mkdocs ([`ab634d7`](https://github.com/Sieboldianus/lbsntransform/commit/ab634d76a14c64fc3d582281190faaa709c5dee7))

* Update mkdocs extensions ([`6a06292`](https://github.com/Sieboldianus/lbsntransform/commit/6a062929cbf00782ec95b57c0af548a33ac4a4bc))

* Minor rephrasing ([`79da4fc`](https://github.com/Sieboldianus/lbsntransform/commit/79da4fc4d0f6e6f53049f0c86f821ff70b70e998))


## v0.12.2 (2020-03-03)

### Ci

* ci: fixup of c7dd9b80 ([`f8dec8c`](https://github.com/Sieboldianus/lbsntransform/commit/f8dec8c008bfb1bd89f338f2f12dd51244518b89))

### Documentation

* docs: add instructions for installing lbsntransform in Linux ([`6ab02ca`](https://github.com/Sieboldianus/lbsntransform/commit/6ab02ca36872fff5803102b0f9aa998a1b6b0a5d))

### Fix

* fix: Module not found when installed with pip in Linux ([`718ae78`](https://github.com/Sieboldianus/lbsntransform/commit/718ae7813195da15eee9ed4297ab7490202dd02b))

* fix: geos not found when installed from conda-forge ([`1c4adcd`](https://github.com/Sieboldianus/lbsntransform/commit/1c4adcd9112be69bb15237712cf427bc1036033a))

### Refactor

* refactor: use input_data instead of reserved class name &#39;input&#39; ([`8cbd6ee`](https://github.com/Sieboldianus/lbsntransform/commit/8cbd6ee76e0220c42dee9c32dd96908e1d70e749))

### Unknown

* add venv to gitignore ([`a6da98b`](https://github.com/Sieboldianus/lbsntransform/commit/a6da98bce2e44f0fcca3fc0c81e311a370894b07))

* Use namespace variable for CI ([`ea75d05`](https://github.com/Sieboldianus/lbsntransform/commit/ea75d05675faadec5103516ba35dce2f9f8e3d4a))

* Use explicit path in CI ([`abd1722`](https://github.com/Sieboldianus/lbsntransform/commit/abd17225a6b5afb47878b3c6470d3ac2596eed08))

* Fix mkdocs CI ([`ed67b46`](https://github.com/Sieboldianus/lbsntransform/commit/ed67b462e166e4bebd96c1439758eb378b1eb31b))

* Fix gitlab ci paths ([`f7b0363`](https://github.com/Sieboldianus/lbsntransform/commit/f7b0363ce1f42f8cfebba828e96a055a26a743a6))


## v0.12.1 (2020-02-11)

### Chore

* chore: add newline (argdown parse) ([`f9e70c3`](https://github.com/Sieboldianus/lbsntransform/commit/f9e70c3f722bea9eaae2fa8e2f9256d3d4818213))

### Ci

* ci: fix argdown process ([`c7dd9b8`](https://github.com/Sieboldianus/lbsntransform/commit/c7dd9b80b3bace53bf666498a80c65d4793ece63))

### Documentation

* docs: clarify --startwith_db_rownumber ([`8a0d44b`](https://github.com/Sieboldianus/lbsntransform/commit/8a0d44b9b5d2e65a9c8d1bac63ccf6c237d2bdeb))

### Fix

* fix: assertion error on records-shard merge

This issue was difficult to debug. Usually, GROUP BY would also return sorted data because PG sorts data by default when using GROUP By. Except that for small arrays, it doesn&#39;t sort. Adding excplicit sort order to make_shard_sql fixes #2 ([`71cf51f`](https://github.com/Sieboldianus/lbsntransform/commit/71cf51f768b5224ee7c432868cec4c36865ab208))

* fix: performance issue with large hll upserts ([`bac72b3`](https://github.com/Sieboldianus/lbsntransform/commit/bac72b3edfe543bb3e5d151cbd40ca1c7afe22e4))

* fix: TypeError for live db query with skip_records ([`b0216a4`](https://github.com/Sieboldianus/lbsntransform/commit/b0216a4172d4203463cb57c9293804b4fff07ab1))

* fix: update lbsnstructure min version ([`371e35d`](https://github.com/Sieboldianus/lbsntransform/commit/371e35d228151b17b8df4970bf1b663fa3190e45))

* fix: add skipping of records based on count ([`383a79b`](https://github.com/Sieboldianus/lbsntransform/commit/383a79be451bb4d707036dc6949fd07e1b60c3a6))

* fix: --startwith_db_rownumber flag ignored on LBSN input ([`4dfa1f3`](https://github.com/Sieboldianus/lbsntransform/commit/4dfa1f3a1ea2f6ba00b1944b2fcda51a03c0fc45))

* fix: cli output reporting (line ending) ([`7ac3c01`](https://github.com/Sieboldianus/lbsntransform/commit/7ac3c01dc72986af2a53c1d95bce593a3a3e1ded))

* fix: add exception handling for hll db queries ([`3ecf721`](https://github.com/Sieboldianus/lbsntransform/commit/3ecf72102817406236a4ce6841b2cf827d452b82))

### Refactor

* refactor: use type alias for LBSNObjects ([`2a8284e`](https://github.com/Sieboldianus/lbsntransform/commit/2a8284e55f8f81fd068cd0e75c6e0b76f89e8a31))

### Unknown

* add insert clear line ([`d92c6d2`](https://github.com/Sieboldianus/lbsntransform/commit/d92c6d25be6b225ae30eb6a23a747fbef72b829c))

* improve reporting ([`ca9f9ec`](https://github.com/Sieboldianus/lbsntransform/commit/ca9f9ec106478ead0627e24f9d6e9500aecb895d))

* update git ignore ([`860abaf`](https://github.com/Sieboldianus/lbsntransform/commit/860abaf94ba82ebe5915d2118458b48447bd422d))

* Merge branch &#39;master&#39; into dev ([`4075c21`](https://github.com/Sieboldianus/lbsntransform/commit/4075c21851858bc6300afeefe694f19c5e44b067))

* Minor typo and formatting ([`da8a014`](https://github.com/Sieboldianus/lbsntransform/commit/da8a01486fb32e9d5904e8ec805435d1df7a5f7e))

* Add code comment ([`b96b9cb`](https://github.com/Sieboldianus/lbsntransform/commit/b96b9cb8e2f2429e571008587ddf1c24d2d86f58))

* typo ([`fd3cfde`](https://github.com/Sieboldianus/lbsntransform/commit/fd3cfdebed49ba3c0a39a9453b5d7f885a20e881))


## v0.12.0 (2020-01-22)

### Feature

* feat: add _emoji_latlng base ([`40634b0`](https://github.com/Sieboldianus/lbsntransform/commit/40634b0a7b8c08e8e673fdb444c992bc69afa87d))

* feat: add cli option to selectively include hll bases ([`bf02a53`](https://github.com/Sieboldianus/lbsntransform/commit/bf02a53d80a47c712564a49c96d88d9933504f86))

* feat: allow lbsn input filtering per type ([`5ce9d6f`](https://github.com/Sieboldianus/lbsntransform/commit/5ce9d6faf767e4aa4390abd2abbf9bbf292828df))

* feat: add composite base example (_latlng_term) ([`9f4b8af`](https://github.com/Sieboldianus/lbsntransform/commit/9f4b8af4f507b7fd72c091c2b9c7397eb7da0c9e))

### Fix

* fix: add origin to lbsn mapping input scheme ([`be7ea94`](https://github.com/Sieboldianus/lbsntransform/commit/be7ea94d22828eaf3bc0f8fd494296d6b1b74d09))

* fix: correct lbsn reference for LBSN mapping ([`dcd096e`](https://github.com/Sieboldianus/lbsntransform/commit/dcd096eb42c2e23f40624684b3061ec3b47c6777))

### Refactor

* refactor: type hints for lbsn bases (use aliases) ([`4ad00d1`](https://github.com/Sieboldianus/lbsntransform/commit/4ad00d14bd79cdbfdc9af92aeac650fb91e8b7ae))

* refactor: type hinting ([`1522b3d`](https://github.com/Sieboldianus/lbsntransform/commit/1522b3d946ca475ec1d2e6288193469c906c2e51))

### Unknown

* fix type hints ([`f038151`](https://github.com/Sieboldianus/lbsntransform/commit/f038151f4d98f794ceb02881d80d6226f59698b2))

* add emoji processing ([`48af6e6`](https://github.com/Sieboldianus/lbsntransform/commit/48af6e619196d8e906c11a84847bc56086bbfb86))

* Update flickr place mapping table ([`9496986`](https://github.com/Sieboldianus/lbsntransform/commit/94969869b69f25608d5133156d77a7a00aea98fa))


## v0.11.0 (2019-12-20)

### Documentation

* docs: Update sequence chart ([`a891edb`](https://github.com/Sieboldianus/lbsntransform/commit/a891edbe30c9ce21ca533d5a4bd6a2c110f4de41))

* docs: add mkdocs Documentation, Examples and Quick Start ([`c7d3d47`](https://github.com/Sieboldianus/lbsntransform/commit/c7d3d477a752ac03623903f8465232266a61ec1f))

### Feature

* feat: Add lbsn to lbsn mapping ([`647fe8b`](https://github.com/Sieboldianus/lbsntransform/commit/647fe8b65584e1dafe5e9a828669bafa93512e98))

* feat: allow zipping of local inputs ([`6ebedf1`](https://github.com/Sieboldianus/lbsntransform/commit/6ebedf1d22fb3c38fb9196e260257cafa32c712d))

* feat: allow skipping until record x ([`3dc34d7`](https://github.com/Sieboldianus/lbsntransform/commit/3dc34d730a205f26a4e5eab967406ca44529deb3))

### Fix

* fix: connection stream abort handling ([`f8a5d1b`](https://github.com/Sieboldianus/lbsntransform/commit/f8a5d1b1765301d24c3f4f9e2445f22662cee8b5))

* fix: yfcc parse error ([`0acc54d`](https://github.com/Sieboldianus/lbsntransform/commit/0acc54d8faaba4e197363c9700111d274813fe93))

* fix: yfcc100m parsing error

(NoneType, but expected one of: int, long) ([`e2f6ae3`](https://github.com/Sieboldianus/lbsntransform/commit/e2f6ae3b839acd5b29a2154adcc23721b734bdac))

* fix: reading stream error

Error while reading records: &lt;class &#39;TypeError&#39;&gt;
unsupported operand type(s) for +: &#39;NoneType&#39; and &#39;list&#39; ([`fe868bc`](https://github.com/Sieboldianus/lbsntransform/commit/fe868bca5081d800e561c1d84540d0d6333d8e09))

### Refactor

* refactor: minor code updates ([`92b6571`](https://github.com/Sieboldianus/lbsntransform/commit/92b65713e3ae1a857ea2759d61803270d5026edf))

### Unknown

* Merge branch &#39;feat-live-import-squashed&#39; into &#39;master&#39;

Feat live import squashed

See merge request lbsn/lbsntransform!4 ([`23a66eb`](https://github.com/Sieboldianus/lbsntransform/commit/23a66eba0d44a188a5699d52499d3e476d047f7c))

* Update sequence diagram ([`6ae7332`](https://github.com/Sieboldianus/lbsntransform/commit/6ae7332cf8e398c3e3ca49f9b669b50720e9734e))

* Minor readme fix ([`9f30964`](https://github.com/Sieboldianus/lbsntransform/commit/9f30964cab18bd4ca085fa5776aa9a7d48e2a292))

* fix bullet list ([`8af45c1`](https://github.com/Sieboldianus/lbsntransform/commit/8af45c1b69842a3b75d6acbce9ea8c50e8ac129b))

* fix markdown linebreaks ([`31418ef`](https://github.com/Sieboldianus/lbsntransform/commit/31418efeb48f0980503dec5d4ede6944a0c4e327))

* Merge branch &#39;dev&#39; ([`e2ce916`](https://github.com/Sieboldianus/lbsntransform/commit/e2ce916a6bc6d7fb0b69eec6764ec14419deb356))

* add reporting of skipped records count ([`ac82b9d`](https://github.com/Sieboldianus/lbsntransform/commit/ac82b9de3f67dfcaf44bb18446d480a1e8c481b0))


## v0.10.2 (2019-11-21)

### Refactor

* refactor: syntax improvements ([`2e30326`](https://github.com/Sieboldianus/lbsntransform/commit/2e303265076629c099092647c3f8b82d3e753f05))

* refactor: improve syntax formatting ([`697dddb`](https://github.com/Sieboldianus/lbsntransform/commit/697dddb41da7bb4e9e829640d4b15900dbe83fb0))

### Unknown

* Remove docker login from ci ([`eb6e028`](https://github.com/Sieboldianus/lbsntransform/commit/eb6e028a6e022195f0eca5fb1866077ed485920b))

* Use full path to registry image in ci ([`37d5d40`](https://github.com/Sieboldianus/lbsntransform/commit/37d5d400bd8139e783d840ebc859c82ef82e68af))

* Add dockerlogin to gitlab-ci ([`57802e7`](https://github.com/Sieboldianus/lbsntransform/commit/57802e727d9b646d34599686036799bf9af89223))

* Merge branch &#39;dev&#39; of gitlab.vgiscience.de:lbsn/lbsntransform into dev ([`7827825`](https://github.com/Sieboldianus/lbsntransform/commit/7827825b0e24c327b66bf051eb49e961ddaaa62c))

* Use local gitlab registry python-ci image ([`a408e47`](https://github.com/Sieboldianus/lbsntransform/commit/a408e4753017213f75e2bb70e1646aea56794b94))


## v0.10.1 (2019-11-20)

### Fix

* fix: invalid call to logger ([`ae16fd7`](https://github.com/Sieboldianus/lbsntransform/commit/ae16fd7fb40714026f65599f1215f2787ff6009b))

### Refactor

* refactor: remove debug code ([`be93f9b`](https://github.com/Sieboldianus/lbsntransform/commit/be93f9b31fbd24cec362a7a6b03d56b3daf9f24b))


## v0.10.0 (2019-11-19)

### Documentation

* docs: update readme ([`e1975a6`](https://github.com/Sieboldianus/lbsntransform/commit/e1975a6fb8f8eb862145befe8efa3da78604b72c))

### Feature

* feat: lbsn raw to hll structure transformation

First part of hll feature implementation

Add hllworker and update bases

refactor: imports and import formatting

hll_add_agg implementation

Merge hll_add_agg results back to records

refactor: use class inheritance for hll bases

refactor: move try..catch to contextmanager

refactor: reduce code duplication in hll.Base classes

refactor: formatting to code conventions

Code separation improvements

feat: allow zipping of multiple web sources

fix: updates

fix: NUL character exception in values

fixup: nul characters

fixup: NUL character

refactor: cleanup &amp; code duplication reduction ([`db1c24e`](https://github.com/Sieboldianus/lbsntransform/commit/db1c24e68c80a2136440ee6a48272f656b923071))

### Refactor

* refactor: untangle classes in helper_functions ([`3a139fa`](https://github.com/Sieboldianus/lbsntransform/commit/3a139fa48efff252158df1d9f32f16fa5f9a5e10))

* refactor: major project structure revision

fix: null geom check ([`b408a6b`](https://github.com/Sieboldianus/lbsntransform/commit/b408a6b6745f8dec976bb4ce4c4caa855b135a4d))

* refactor: cleanup cli args and config formatting ([`104c53c`](https://github.com/Sieboldianus/lbsntransform/commit/104c53c4b62d2cc62756fe91959cb98c32cdf2c4))

* refactor: cleanup cli args and config formatting ([`c2f6537`](https://github.com/Sieboldianus/lbsntransform/commit/c2f6537d005a63e2033eb8f5d8f35ebd2569efd8))

* refactor: use variable for null_geom ([`49d859a`](https://github.com/Sieboldianus/lbsntransform/commit/49d859a43c2fd4d2897669e86416dcf68a05aad7))

### Unknown

* fix readme ([`765453f`](https://github.com/Sieboldianus/lbsntransform/commit/765453fafc577191c3b05940549b74375e1501a4))

* fix links in readme ([`24da601`](https://github.com/Sieboldianus/lbsntransform/commit/24da601ab356cd644801f0a6b00e3cd64b6a76d5))

* Merge branch &#39;dev-hll&#39; into dev ([`fa903b4`](https://github.com/Sieboldianus/lbsntransform/commit/fa903b442738bafbd3c67bec850ea434271f3574))

* Pin lbsnstructure in chore ([`5525be0`](https://github.com/Sieboldianus/lbsntransform/commit/5525be0cf3b2a30248cc694d9495e7216acfcb6c))

* Merge branch &#39;master&#39; of github.com:Sieboldianus/lbsntransform ([`60ca66e`](https://github.com/Sieboldianus/lbsntransform/commit/60ca66efc02161235f4b521d407cb91cbaba0d71))


## v0.9.1 (2019-10-23)

### Fix

* fix: pin lbsnstructure version ([`c74644c`](https://github.com/Sieboldianus/lbsntransform/commit/c74644cd1861f7f0a3357020e646421dbf2e0630))


## v0.9.0 (2019-10-23)

### Feature

* feat: migrations to lbsnstructure v1.3.0 ([`acbed1b`](https://github.com/Sieboldianus/lbsntransform/commit/acbed1b2baa65635104f7ff0a05562c6c9cca2a7))


## v0.8.3 (2019-10-21)

### Fix

* fix: missing coalesce for place_description ([`c6457d5`](https://github.com/Sieboldianus/lbsntransform/commit/c6457d5db724b8b37b72c6f82b3f1bbde1dfa05a))

* fix: catch empty proto_map ([`23559d5`](https://github.com/Sieboldianus/lbsntransform/commit/23559d5da3f705563ed318d62713352deef4e7ac))

### Unknown

* substitute description from about on empty ([`0bd58aa`](https://github.com/Sieboldianus/lbsntransform/commit/0bd58aa82e7abac89b76d4c2e6ebd09d89f61d5a))


## v0.8.2 (2019-09-17)

### Fix

* fix: add support for postgres hstore ([`8c99a19`](https://github.com/Sieboldianus/lbsntransform/commit/8c99a19770f390c77f11223ae5ee3b3424757aa5))

### Unknown

* Update place attributes ([`3d1af08`](https://github.com/Sieboldianus/lbsntransform/commit/3d1af086d3211afbdc80cfbed97281618dca28e0))

* initial facebook place graph mapping ([`cbcd1d8`](https://github.com/Sieboldianus/lbsntransform/commit/cbcd1d8fede8405de4148886a92d69fc9621218b))


## v0.8.1 (2019-09-17)

### Chore

* chore: enable file name report log ([`88862dd`](https://github.com/Sieboldianus/lbsntransform/commit/88862dd7d180381baa9ab8d781fd89c816d32c7e))

* chore: use main conda image for gitlab ([`0a91790`](https://github.com/Sieboldianus/lbsntransform/commit/0a917900c7b5e268db9a07524f6ef6ed98ea9099))

* chore: fix conda not available in latest continuum image ([`9587363`](https://github.com/Sieboldianus/lbsntransform/commit/9587363a6f9fecc44254a8c13815be4389c1087c))

* chore: update conda container ([`b66c148`](https://github.com/Sieboldianus/lbsntransform/commit/b66c148bd63f45236ef822629ae06d7abeed8df2))

* chore: update gitlab-ci conda config ([`0c79a37`](https://github.com/Sieboldianus/lbsntransform/commit/0c79a37a8dd017805607ecfdd700440befb5b356))

### Fix

* fix: correct close of log file ([`c75d115`](https://github.com/Sieboldianus/lbsntransform/commit/c75d1157cec5955f1a0fa8a5e91c097ba0a25a29))

* fix: return records for json.load wrapper ([`472e3d2`](https://github.com/Sieboldianus/lbsntransform/commit/472e3d2e484c154b35bded3850f70595e36269c9))

* fix: catch jsonDecodeError on read; wrap exceptions ([`64888cf`](https://github.com/Sieboldianus/lbsntransform/commit/64888cf16db47878d5b721224befd87cff5ea12a))

* fix: improve uncought exception reporting ([`22cc420`](https://github.com/Sieboldianus/lbsntransform/commit/22cc4207346d1c37146adc4527468c7865d92ef5))

* fix: CSV iterator ([`c372431`](https://github.com/Sieboldianus/lbsntransform/commit/c372431c0dacfaf573f015d1773e019417f94163))

* fix: flickr mapping return pipe ([`393d708`](https://github.com/Sieboldianus/lbsntransform/commit/393d708172014f65acf964257b7392fffe51f2a7))

* fix: handling of empty language in twitter json parse ([`bee811c`](https://github.com/Sieboldianus/lbsntransform/commit/bee811c12eba85dde57350ca50981e7a0a784188))

### Refactor

* refactor: separate logging formatter for JSon exceptions ([`6db6b2c`](https://github.com/Sieboldianus/lbsntransform/commit/6db6b2c9af7386e67b2e766bb256ba7a3cf51b96))

### Unknown

* append log, if already exists ([`320c4cf`](https://github.com/Sieboldianus/lbsntransform/commit/320c4cfc1d2e1844b094dd4db52780d826b3f51d))

* improve logging statistics ([`7391712`](https://github.com/Sieboldianus/lbsntransform/commit/73917128f1949e933fbf23f2f92904b60462fe47))

* concatenate log files per day ([`d7685e5`](https://github.com/Sieboldianus/lbsntransform/commit/d7685e5ac9554f90a728565918b8574befcd0648))

* remove trailing input() in cli-mode ([`9481dc1`](https://github.com/Sieboldianus/lbsntransform/commit/9481dc18331706040c994cf977436fbc88b8f97f))

* fixup: close log handlers ([`78756c2`](https://github.com/Sieboldianus/lbsntransform/commit/78756c2aa547b58f786fde3758113a10c7add20d))

* fixup: use correct logging reference ([`f7ee594`](https://github.com/Sieboldianus/lbsntransform/commit/f7ee5945885a0a780c56bb408411e4ad9e1ac2fb))

* fixup error reporting ([`6564ca9`](https://github.com/Sieboldianus/lbsntransform/commit/6564ca953e04769f712edea2819bac14cef01dd9))

* Merge branch &#39;master&#39; into dev ([`beaf45b`](https://github.com/Sieboldianus/lbsntransform/commit/beaf45b3a101b9ed955e9af7fb88fb2cbfd8ca12))


## v0.8.0 (2019-08-22)

### Chore

* chore: disable no member pylint ([`02bd777`](https://github.com/Sieboldianus/lbsntransform/commit/02bd7773662b072b4d674d8f7d3ace788d99e815))

### Feature

* feat: add option to process line separated json ([`6300838`](https://github.com/Sieboldianus/lbsntransform/commit/630083862c5d4df126b3ccc1520fd2061bb26e48))

### Fix

* fix: reporting of count_glob and identified records ([`7feb38a`](https://github.com/Sieboldianus/lbsntransform/commit/7feb38ae75a6013cbb864ebccba32e666de3a4dd))

* fix: RepeatedCompositeField Error in Windows and MacOS ([`dc87e87`](https://github.com/Sieboldianus/lbsntransform/commit/dc87e87c77357da58a531ba049bcc000cbccb651))

* fix: Twitter tweet parsing structure update ([`7d19357`](https://github.com/Sieboldianus/lbsntransform/commit/7d193574af40544353f35816bfa87f1d1aa16672))

* fix: wrong reporting of processed records ([`fcf0dd8`](https://github.com/Sieboldianus/lbsntransform/commit/fcf0dd86621e55ba127b7a283ffd3a062c39e8d3))

* fix: record pipeline to return only single records ([`8bd895a`](https://github.com/Sieboldianus/lbsntransform/commit/8bd895a32477c8774c4c0895866ccf700e00cb38))

* fix: database rollback integrity error ([`969b482`](https://github.com/Sieboldianus/lbsntransform/commit/969b482e5a06456db946d28cc76f457e7102b3bf))

* fix: use pathlib for os independent path handling ([`0d12c9e`](https://github.com/Sieboldianus/lbsntransform/commit/0d12c9e41fe5622a434fbdee65565021b348ca38))

* fix: recognize transfer_limit ([`1fd9bde`](https://github.com/Sieboldianus/lbsntransform/commit/1fd9bdebcb40693d3b9bd9a7f7a3525e06f4b66a))

* fix: add exception handling for database out of space ([`977517e`](https://github.com/Sieboldianus/lbsntransform/commit/977517ee73a9cc8e468a5d17304da9b42e04d348))

### Refactor

* refactor: extract functions and follow type conventions ([`25df83f`](https://github.com/Sieboldianus/lbsntransform/commit/25df83fa65ec37f8a58f9702cce552e036033767))

* refactor: update to latest lbsnstructure ([`95c80e6`](https://github.com/Sieboldianus/lbsntransform/commit/95c80e6cbe686f7ffadac6d8cfc27561fb045986))

### Unknown

* Merge branch &#39;dev&#39; ([`a1e0fea`](https://github.com/Sieboldianus/lbsntransform/commit/a1e0fea993a2846384a64d6e69800ecf808ebfdb))

* Update config docs on revursive load info ([`fdcf138`](https://github.com/Sieboldianus/lbsntransform/commit/fdcf138256784db4674bec2c9661660fc0da7ada))

* Update for ignoreing scripts/ ([`a849427`](https://github.com/Sieboldianus/lbsntransform/commit/a849427bb8ab0d26242097a76029f3c246c509fc))


## v0.7.3 (2019-07-12)

### Documentation

* docs(readme): update command line args info ([`62a04cf`](https://github.com/Sieboldianus/lbsntransform/commit/62a04cf028577691aa41e10ed0dd2563af3eb094))

### Fix

* fix: do not overwrite with Null-Island Geometry ([`65788a6`](https://github.com/Sieboldianus/lbsntransform/commit/65788a67ad042a628bc36153cbe14eed808e6d10))

* fix: typo ([`8fc1769`](https://github.com/Sieboldianus/lbsntransform/commit/8fc176931313c7c87be15c5c0b0aff71dc2a2768))

### Unknown

* Merge branch &#39;dev&#39; ([`3b1a698`](https://github.com/Sieboldianus/lbsntransform/commit/3b1a69867cc1b1ecb6954736c83851d3cd486eae))

* fix typo in args list ([`dfe599f`](https://github.com/Sieboldianus/lbsntransform/commit/dfe599f0c62e40dc29131364f0b7756645e03da0))

* Merge branch &#39;dev&#39; ([`ee7a1ad`](https://github.com/Sieboldianus/lbsntransform/commit/ee7a1ad3b9140540fb5dd37be84541fac0df75fe))

* fix typo in args list ([`8f0954f`](https://github.com/Sieboldianus/lbsntransform/commit/8f0954f89977230660d46f6a2562b66c3a6837b5))

* Merge branch &#39;dev&#39; ([`69f316a`](https://github.com/Sieboldianus/lbsntransform/commit/69f316a04b571061b089c2d1c505ecce6324d6e1))


## v0.7.2 (2019-07-12)

### Fix

* fix: pipeline handle for different input queries ([`fbbfa1f`](https://github.com/Sieboldianus/lbsntransform/commit/fbbfa1f7803e63d3c8871588944d94371aa29edd))

* fix: pipeline generators for local file loop ([`4f62a70`](https://github.com/Sieboldianus/lbsntransform/commit/4f62a70bf718c732e9f65a01b9e1b3af081fe3fb))

* fix: reporting for local input loop count ([`0cc4a2e`](https://github.com/Sieboldianus/lbsntransform/commit/0cc4a2e70b91205c88575da01a8580106c65771d))

* fix: json local input array parse ([`928952d`](https://github.com/Sieboldianus/lbsntransform/commit/928952d1d3714e63779231d84f9f5ff49883cfde))

* fix: store final remaining records ([`f789a1e`](https://github.com/Sieboldianus/lbsntransform/commit/f789a1e2432db348070250c720e0a500cda7a927))

### Refactor

* refactor: simplify main loop ([`6b3912f`](https://github.com/Sieboldianus/lbsntransform/commit/6b3912f54b95b9a67d51dec200b89a517ff9ae98))

* refactor: rename protected dict ([`c421f7b`](https://github.com/Sieboldianus/lbsntransform/commit/c421f7b9568cffb4c8f44e24217a9650e794efa8))

### Unknown

* remove file reporting ([`0f28368`](https://github.com/Sieboldianus/lbsntransform/commit/0f28368747f47836b06cdfdf290863dd6da36675))

* remove orphan counters ([`7ea800b`](https://github.com/Sieboldianus/lbsntransform/commit/7ea800b45deae83cd166883f07d1051e10a2d727))

* add timestamp to protobuf func ([`c674eab`](https://github.com/Sieboldianus/lbsntransform/commit/c674eab77f95691da546ead7eaf356ad5ca195f7))


## v0.7.1 (2019-06-11)

### Fix

* fix: on update do not overwrite with default ([`9d3de9d`](https://github.com/Sieboldianus/lbsntransform/commit/9d3de9dba08e556cf2bd045c515c816f3afad14a))

* fix: store origin_id before any insert ([`55df1b1`](https://github.com/Sieboldianus/lbsntransform/commit/55df1b1f2a870acf01b04a8c6e5d66cfb1963a5c))


## v0.7.0 (2019-06-10)

### Chore

* chore: add requests and update dependencies ([`9a9089f`](https://github.com/Sieboldianus/lbsntransform/commit/9a9089f415cccef62e87d6f990343dfa96ebeacf))

### Documentation

* docs: update readme link to protobuf spec ([`8d72df0`](https://github.com/Sieboldianus/lbsntransform/commit/8d72df0d447433f4ce9d55f21fc6e271f879ce91))

### Feature

* feat: add yfcc100m place data mapping ([`2245fc3`](https://github.com/Sieboldianus/lbsntransform/commit/2245fc3e6b2ca2557f91f15b30bb76a6d3bbdadb))

### Fix

* fix: remove wrong place id column, update photo id ([`fbca35d`](https://github.com/Sieboldianus/lbsntransform/commit/fbca35d0ec1f7e1c9e3e6f7ffa32a2830b6ed610))

### Refactor

* refactor: clean up imports ([`f88084e`](https://github.com/Sieboldianus/lbsntransform/commit/f88084eb191cf12bf65d05937bfb70dc1bc7834a))

### Unknown

* Update handlers for default values and null geometry ([`f1582a9`](https://github.com/Sieboldianus/lbsntransform/commit/f1582a94803b42b90474e7ef5ffc8170d855859c))


## v0.6.0 (2019-06-03)

### Chore

* chore: add gitlab ci for basic test and badges ([`5d04980`](https://github.com/Sieboldianus/lbsntransform/commit/5d0498085f9696541c5e3dafd2f7a471ab9d1ba6))

### Documentation

* docs: update readme badges ([`7797196`](https://github.com/Sieboldianus/lbsntransform/commit/77971969ae7c73033cf1e834cf074daf2bcbaf9f))

### Feature

* feat: allow streaming web input source ([`64ad913`](https://github.com/Sieboldianus/lbsntransform/commit/64ad913a4ac9e1b293715683d5a158e733ad15b2))

### Fix

* fix: add bitarray for gitlab ci dev yml ([`5baf21c`](https://github.com/Sieboldianus/lbsntransform/commit/5baf21c000e83cb08bb6fe9c64389e7898475fdb))

### Unknown

* fix badge links ([`e9424f7`](https://github.com/Sieboldianus/lbsntransform/commit/e9424f7d99204ad6b43abef4803e96aee9d53355))

* Merge branch &#39;dev&#39; ([`4c7a557`](https://github.com/Sieboldianus/lbsntransform/commit/4c7a557277b9069627fa9df3a5f49a7eb840757f))

* update version ([`74717b2`](https://github.com/Sieboldianus/lbsntransform/commit/74717b2a258b52209fe98d073f498d0e307f32a3))


## v0.5.0 (2019-06-03)


## v0.4.0 (2019-06-03)

### Chore

* chore: disable pylint messages ([`c337eaa`](https://github.com/Sieboldianus/lbsntransform/commit/c337eaa56831748337543c90eafb178f877f0d65))

* chore: file mode changes WSL ([`735887c`](https://github.com/Sieboldianus/lbsntransform/commit/735887cf2e7e85fc94cef468ae507e3e53833289))

* chore: add environment_dev.yml for dev deps ([`12466ef`](https://github.com/Sieboldianus/lbsntransform/commit/12466efd282852c0de4ae6835c868132f52fa6b5))

### Feature

* feat: Flickr import revise functions ([`4d07673`](https://github.com/Sieboldianus/lbsntransform/commit/4d07673849a819273c30273c25d96db13cbe2721))

* feat: add importer class for YFCC100M dataset ([`f138f90`](https://github.com/Sieboldianus/lbsntransform/commit/f138f9062f61fd6d2fefeaa6f737bc44349ba44d))

* feat: add option to specify postgres port ([`293e3cf`](https://github.com/Sieboldianus/lbsntransform/commit/293e3cf88a74ea33b70050397e20220b5aacf84c))

### Fix

* fix: pathlib glob update ([`4b979d5`](https://github.com/Sieboldianus/lbsntransform/commit/4b979d57d9b018635ab4d53a2b2679bc6904716d))

* fix: remove lbsntransform from dev yaml ([`51b5ec7`](https://github.com/Sieboldianus/lbsntransform/commit/51b5ec7c769c271c94e0950cf27acdf500bf1007))

* fix: bug ([`d8f711c`](https://github.com/Sieboldianus/lbsntransform/commit/d8f711cb785a537c3fe7d0de03b716349ee0ff6d))

* fix: use list for lbsn_records ([`7957c39`](https://github.com/Sieboldianus/lbsntransform/commit/7957c3988a819dce92540189371b1a1a7a3882b4))

* fix: correct field for post_guid and add place_guid ([`bfc4c21`](https://github.com/Sieboldianus/lbsntransform/commit/bfc4c219153d7f59180de0e308360ccaaea30899))

* fix: missing input args ([`f0c3337`](https://github.com/Sieboldianus/lbsntransform/commit/f0c3337b881683bbb29f70ba09967d0acf3665bb))

### Refactor

* refactor: clean up comments ([`cee0027`](https://github.com/Sieboldianus/lbsntransform/commit/cee0027ec70fe1e3ecb146353cce8b3145413b54))

* refactor: major refactor for pipe processing ([`f99397b`](https://github.com/Sieboldianus/lbsntransform/commit/f99397b3bc75cb89394dd6a8ea0c3ec83fe8ecea))

* refactor: code conventions ([`485010f`](https://github.com/Sieboldianus/lbsntransform/commit/485010f7da23b7cbe8a01882752258a6050d5039))

* refactor: add ip-port split function ([`2678467`](https://github.com/Sieboldianus/lbsntransform/commit/2678467d2aa20cfaceff1df295b5cfbb316b2c74))

* refactor: add docstrings ([`706d379`](https://github.com/Sieboldianus/lbsntransform/commit/706d379407f4c0054afb6aafd9041666effebaa0))

* refactor: use pathlib for cross-system compatibility ([`b7265d6`](https://github.com/Sieboldianus/lbsntransform/commit/b7265d69fd270196df00741970a221b2ca557e2d))

* refactor: basic code improvements ([`66fa778`](https://github.com/Sieboldianus/lbsntransform/commit/66fa7789ec8e30a9718b5a1e0c5b745be6bb8ed5))

* refactor(cx_setup): code conventions ([`b7e32ef`](https://github.com/Sieboldianus/lbsntransform/commit/b7e32ef5b4ed8bd461dd5ca6e2b58824c8a4442b))

### Style

* style: move imports to head of file ([`ef3a6fb`](https://github.com/Sieboldianus/lbsntransform/commit/ef3a6fb7fbed246ffb0559a50934fb41d3dbdfd7))

### Unknown

* fix increase csv field size limit ([`0f19001`](https://github.com/Sieboldianus/lbsntransform/commit/0f19001f0a0c3075c4decc164b67a0adcc4455bb))

* update comment ([`9a7be6f`](https://github.com/Sieboldianus/lbsntransform/commit/9a7be6f583273a944bd679c94023954f8c77e654))

* Remove re package as it is not needed (see regex) ([`fe2b1e0`](https://github.com/Sieboldianus/lbsntransform/commit/fe2b1e07ca837a0af7dc52549f8a50b56e8df5b2))


## v0.3.21 (2019-01-11)

### Fix

* fix: input cursor ref without connection ([`6b01fc5`](https://github.com/Sieboldianus/lbsntransform/commit/6b01fc52222a44a637ccc33bc1c95bb1d3cf235d))


## v0.3.20 (2019-01-11)

### Fix

* fix:  remove hardcoding of exclude city and country geoaccuracy posts

- this is now possible through the use
of min_geoaccuracy input arg
- includes a number of style improvements ([`5956da2`](https://github.com/Sieboldianus/lbsntransform/commit/5956da2bd8e4d564446fec5c61e2107007f22bca))

### Style

* style: minor code style updates (pylint) ([`04e797f`](https://github.com/Sieboldianus/lbsntransform/commit/04e797f69e3def60d7e2f8ed6bfbdc26bc785ff0))


## v0.3.19 (2019-01-09)

### Fix

* fix:  include srid for WKT bug

- related to how shapely handles WKT by default
- also fixed a number of issues and updated style conventions ([`fe0ffaa`](https://github.com/Sieboldianus/lbsntransform/commit/fe0ffaa6b43a7e510aade2a381a5d99ab189dae8))

### Unknown

* bug found in null geometry ([`eaf85ba`](https://github.com/Sieboldianus/lbsntransform/commit/eaf85ba1f6e4271948898cbfdc222b25de8d11e9))


## v0.3.18 (2019-01-06)

### Fix

* fix: auto versioning ([`0187582`](https://github.com/Sieboldianus/lbsntransform/commit/0187582b52e12bee9aaa24b787c9f7480ee042bb))


## v0.3.17 (2019-01-06)

### Fix

* fix: versioning ([`ed3c4c7`](https://github.com/Sieboldianus/lbsntransform/commit/ed3c4c730a3b64b76bbd7b4502a95fa6526fb117))


## v0.3.16 (2019-01-06)

### Fix

* fix: versioning ([`5c213df`](https://github.com/Sieboldianus/lbsntransform/commit/5c213df1b5981e9aa8bfc24ed2935e0c37f03565))


## v0.3.15 (2019-01-06)

### Fix

* fix: auto versioning ([`ec2252f`](https://github.com/Sieboldianus/lbsntransform/commit/ec2252f97667aedaccbdd77659a29bb87afc8cd8))


## v0.3.14 (2019-01-06)

### Fix

* fix: auto versioning ([`785f54f`](https://github.com/Sieboldianus/lbsntransform/commit/785f54f88ac355d84328f9b0821484ac3cd73983))


## v0.3.13 (2019-01-06)

### Fix

* fix: auto versioning ([`d42210f`](https://github.com/Sieboldianus/lbsntransform/commit/d42210f84da4245bfcfc7e2008a747e6875c0e47))


## v0.3.12 (2019-01-06)

### Fix

* fix: auto versioning ([`7fbb876`](https://github.com/Sieboldianus/lbsntransform/commit/7fbb8765f6f1e1ce48bf73c5242cd20350f37046))


## v0.3.11 (2019-01-06)

### Fix

* fix(cx_setup): use correct target name ([`e7ac3fd`](https://github.com/Sieboldianus/lbsntransform/commit/e7ac3fdfb1fa4e6172273ac57f6809324fd10f59))


## v0.3.10 (2019-01-06)

### Fix

* fix(cx_setup): added correct version ref ([`a18bee4`](https://github.com/Sieboldianus/lbsntransform/commit/a18bee4c995e10c71820fb9d063b5768ea4ba4a3))


## v0.3.9 (2019-01-06)

### Fix

* fix(shared_structure): auto versioning ([`9265caf`](https://github.com/Sieboldianus/lbsntransform/commit/9265cafa75650024242cfb67648f5230fc1cb900))


## v0.3.8 (2019-01-06)

### Fix

* fix(shared_structure): auto versioning ([`19d7128`](https://github.com/Sieboldianus/lbsntransform/commit/19d7128a8a989512f5e799b095ff1c787f83b33e))


## v0.3.7 (2019-01-05)

### Fix

* fix: auto version ([`0d17d78`](https://github.com/Sieboldianus/lbsntransform/commit/0d17d78bc40961908a4debcd6810fbceca3cf060))


## v0.3.6 (2019-01-05)

### Fix

* fix: auto version ([`a7df4c5`](https://github.com/Sieboldianus/lbsntransform/commit/a7df4c538110206170c9b93ef70817148d0f9162))


## v0.3.5 (2019-01-05)

### Fix

* fix: auto version ([`dc2a81a`](https://github.com/Sieboldianus/lbsntransform/commit/dc2a81ac178fd3c4ca604ff87964cf01d203c00f))


## v0.3.4 (2019-01-05)

### Fix

* fix: auto version ([`eee49c0`](https://github.com/Sieboldianus/lbsntransform/commit/eee49c0da2f937ccd6251a3c71c1421e7aa6ab10))


## v0.3.3 (2019-01-05)

### Fix

* fix: auto version ([`906dbb7`](https://github.com/Sieboldianus/lbsntransform/commit/906dbb781f9b0a209f5f599551936917b476718e))


## v0.3.2 (2019-01-05)

### Fix

* fix: update autpo version ([`f1dd51d`](https://github.com/Sieboldianus/lbsntransform/commit/f1dd51df4b5b9bf97c6455add26ea89d00211f3f))

### Unknown

* fix (shared_structure):  added docstrings ([`e26bc35`](https://github.com/Sieboldianus/lbsntransform/commit/e26bc35a9f2438deb3ce31218bc65f8a6aa749b8))

* feat (shared_structure): allow initializing empty structures

- e.g. used in Tag Maps  package
- this update also changes class references,
due to proper Capital Letters ([`d4fdb01`](https://github.com/Sieboldianus/lbsntransform/commit/d4fdb015fe5d4878f1d1a080061bb8a5580c06fc))


## v0.3.1 (2019-01-04)

### Fix

* fix: auto changelog ([`3f7ff5e`](https://github.com/Sieboldianus/lbsntransform/commit/3f7ff5e35171589df92fc69649f4a301e6a1efaf))


## v0.3.0 (2019-01-04)

### Feature

* feat: add auto changelog ([`926cb20`](https://github.com/Sieboldianus/lbsntransform/commit/926cb201bd876b8d196de6ba1cf3f63e7ec29a5d))

### Unknown

* Feat: add auto changelog ([`2eb510d`](https://github.com/Sieboldianus/lbsntransform/commit/2eb510dcb9200d0492e9f6b0f96103b57241a2ee))

* doc: added docstring to setup.py ([`d1d7e89`](https://github.com/Sieboldianus/lbsntransform/commit/d1d7e89b95fdffbb8e84720fcb6766ffa3176060))


## v0.2.0 (2019-01-04)

### Feature

* feat: implement semantic versioning ([`41447eb`](https://github.com/Sieboldianus/lbsntransform/commit/41447eb1805f11df696016f049c1be5cdbe51df5))


## v0.1.22 (2019-01-04)

### Fix

* fix: crlf line endings ([`148550d`](https://github.com/Sieboldianus/lbsntransform/commit/148550d6e756544002d4f74f6cf84050a91e6038))

### Unknown

* Fix line endings ([`f741318`](https://github.com/Sieboldianus/lbsntransform/commit/f741318be6cae72a5206ab7311b1c68ea1a6f187))


## v0.1.21 (2019-01-04)

### Fix

* fix: markdown description bug
https://github.com/pypa/warehouse/issues/3664
https://github.com/pypa/twine/issues/425 ([`5161f94`](https://github.com/Sieboldianus/lbsntransform/commit/5161f94c9972a8f13eaf2ec91c2c1af8d8482afc))


## v0.1.20 (2019-01-04)

### Fix

* fix: pypi upload 7 ([`13e335a`](https://github.com/Sieboldianus/lbsntransform/commit/13e335ae91da681f9938abe4b27dc58734c85c1f))


## v0.1.19 (2019-01-04)

### Fix

* fix: pypi upload 6 ([`6efe686`](https://github.com/Sieboldianus/lbsntransform/commit/6efe686f37124fe3b4d2395805fe815401ecd765))


## v0.1.18 (2019-01-04)

### Fix

* fix: pypi upload 5 ([`5c1533c`](https://github.com/Sieboldianus/lbsntransform/commit/5c1533c9cf3db56a183c7dddbbf9c8f4c4dd0459))


## v0.1.17 (2019-01-04)

### Fix

* fix: pypi upload 4 ([`75e8453`](https://github.com/Sieboldianus/lbsntransform/commit/75e84533155f9c8185f73bb724c60f0dab7369b0))


## v0.1.16 (2019-01-04)

### Fix

* fix: pypi upload 3 ([`7a8d88a`](https://github.com/Sieboldianus/lbsntransform/commit/7a8d88a3ba8ff244027b284175bd77831d67346b))


## v0.1.15 (2019-01-04)

### Fix

* fix: pypi upload 2 ([`d09b7d0`](https://github.com/Sieboldianus/lbsntransform/commit/d09b7d00cb54c741dd8aac4e03aa3e66baa10288))


## v0.1.14 (2019-01-04)

### Fix

* fix: pypi upload ([`be9fee3`](https://github.com/Sieboldianus/lbsntransform/commit/be9fee3c34abae1eb6132677579b4adb4e7345df))


## v0.1.13 (2019-01-04)

### Fix

* fix: setup.py version file ref ([`979d6e7`](https://github.com/Sieboldianus/lbsntransform/commit/979d6e7b975fdd8249b288d3ce5b08cd1aed76c1))


## v0.1.12 (2019-01-04)

### Fix

* fix: versioning publish 4 ([`888a584`](https://github.com/Sieboldianus/lbsntransform/commit/888a584d55590ecbc415a208e1eeeadf93bdd57c))


## v0.1.11 (2019-01-04)

### Fix

* fix: versioning publish 3 ([`a3c0118`](https://github.com/Sieboldianus/lbsntransform/commit/a3c01181c6e650d08765f2120b80e824616b603b))


## v0.1.10 (2019-01-04)

### Fix

* fix: versioning publish 2 ([`ac0bbe3`](https://github.com/Sieboldianus/lbsntransform/commit/ac0bbe3a55d3a902fd6c7287dad29dd52cf74b55))


## v0.1.9 (2019-01-04)

### Fix

* fix: versioning publish ([`fb52e02`](https://github.com/Sieboldianus/lbsntransform/commit/fb52e020c9d70bdfeda33c238e3a71da0e41f329))


## v0.1.8 (2019-01-04)

### Fix

* fix: versioning ([`62e664f`](https://github.com/Sieboldianus/lbsntransform/commit/62e664f3c09b65cb15b10672520bc204d2690a35))


## v0.1.7 (2019-01-04)

### Unknown

* Test version ([`4eec640`](https://github.com/Sieboldianus/lbsntransform/commit/4eec640d29e30b74a0ab9eb19148a1284d8df232))


## v0.1.603 (2019-01-04)

### Fix

* fix: semantic-release versioning ([`f29b9dc`](https://github.com/Sieboldianus/lbsntransform/commit/f29b9dc53541d2391acfb35813e6f62916ea01d3))


## v0.1.601 (2019-01-04)

### Feature

* feat: add semantic-release version control
- increased version ([`a54c9f2`](https://github.com/Sieboldianus/lbsntransform/commit/a54c9f2b85ee1474b0e5e43f720d37c95d720b95))

### Fix

* fix: increase version number in main.py too ([`f88b408`](https://github.com/Sieboldianus/lbsntransform/commit/f88b408af37fd3d0e7391151cabaa8e00f94859c))


## v0.1.600 (2019-01-03)

### Unknown

* Increased version to 0.1.600 ([`36b0758`](https://github.com/Sieboldianus/lbsntransform/commit/36b0758818d6890536946ee0544e98e1c8db24c4))

* Minor bugfixes due to code refactor
- added docstrings to modules ([`52608e4`](https://github.com/Sieboldianus/lbsntransform/commit/52608e421fc563ab3b59b5ffdc31123d529ad269))

* Refactored main, config; tested &amp; bugfixes ([`da20640`](https://github.com/Sieboldianus/lbsntransform/commit/da206407d1c65df7e89fbc23390e2a071c8f6109))

* Additional code refactor for matching conventions
- submit_data class
- pep8 conformity ([`e27786a`](https://github.com/Sieboldianus/lbsntransform/commit/e27786a89f1a5a0bc410566e4722ea2e7b6810e7))

* refactored main to pep8 ([`0679c00`](https://github.com/Sieboldianus/lbsntransform/commit/0679c00a32ec4758a550af4df9791369663a8c57))

* more code refactorings according to pep8 ([`3f1645f`](https://github.com/Sieboldianus/lbsntransform/commit/3f1645f3bb1dbb6f0c8a8efcebcd5da65cd143e4))

* Refactored to snake style additional ([`1a87553`](https://github.com/Sieboldianus/lbsntransform/commit/1a8755370e19c0147b495d79c1fd667537efce27))

* refactored HF and twitter mapping to snake style code convention ([`fed1a4b`](https://github.com/Sieboldianus/lbsntransform/commit/fed1a4b1c742f700e93f62046d139035bb1e132b))

* Minor refactoring based on VSCode Move ([`e34af34`](https://github.com/Sieboldianus/lbsntransform/commit/e34af34382c8fed7cfe2801c1ff171f8850fbac8))

* Fixed reference bug for local file input ([`94e5362`](https://github.com/Sieboldianus/lbsntransform/commit/94e5362f9e2d90ce25022685760cf8286cf9b043))

* Fixed 2 issues with parsing incomplete twitter jsons
- no country code
- no bounding box ([`bd6ab20`](https://github.com/Sieboldianus/lbsntransform/commit/bd6ab20751e470df6828cdd3092e4985cb694698))

* Updated gitignore, changed Line endings CRLF to LF ([`b702b5d`](https://github.com/Sieboldianus/lbsntransform/commit/b702b5d668c3531d71eb03689bbf195ed240148a))

* Increased version, fixed merge conflicts ([`6390146`](https://github.com/Sieboldianus/lbsntransform/commit/63901462809a88da245481134640c8a874896106))


## v0.1.521 (2018-12-23)

### Unknown

* Fixed dev merge ([`6bc62a1`](https://github.com/Sieboldianus/lbsntransform/commit/6bc62a1384ceedd0ba301431b28c39cd5260e9cf))

* Added min geoaccuracy functions
- needs to be checked with Flickr mapping
- main() needs to be cleaned up, better organisation of reporting statistics ([`f62bade`](https://github.com/Sieboldianus/lbsntransform/commit/f62badea41e4ce9807ac9fd4680fdd33c2877a27))

* Style improvements ([`59b9be6`](https://github.com/Sieboldianus/lbsntransform/commit/59b9be65479fb62c4f9ade91bf20e72ec602158a))


## v1.5.20 (2018-12-19)

### Unknown

* Increased version ([`10acf9c`](https://github.com/Sieboldianus/lbsntransform/commit/10acf9c16577a9f497313c824e2dbd42cee4cf9f))

* Fixed geocode-bug ([`a35cf87`](https://github.com/Sieboldianus/lbsntransform/commit/a35cf873a65b79e063e161c8c9bcd24e618b4e58))

* Fixed geocode bug ([`31e5023`](https://github.com/Sieboldianus/lbsntransform/commit/31e50230871198e369a2ab9ee79ff841e46ab0ba))

* Reverted import version ([`85cac0a`](https://github.com/Sieboldianus/lbsntransform/commit/85cac0a843059094aa7bd0e10d4d33d08ad4ec8b))


## v0.1.518 (2018-12-19)

### Unknown

* Increased version ([`e8e3ee8`](https://github.com/Sieboldianus/lbsntransform/commit/e8e3ee80d218c91ffc4d70cdabe15114bff15b35))

* Merge branch &#39;dev&#39;

Fixed proto-composite-bug ([`05628c4`](https://github.com/Sieboldianus/lbsntransform/commit/05628c4e40be2efc52bcbef198f82480c4134b2b))

* Fixed protocoll buffers bug
(Repeated Composite Container ([`5097d6b`](https://github.com/Sieboldianus/lbsntransform/commit/5097d6b84204615927660412385e2b64547caddc))

* Merge branch &#39;dev&#39;

Hotfix ignore reactions ([`16a3bc8`](https://github.com/Sieboldianus/lbsntransform/commit/16a3bc85db93b3c5e398ccda4e6072ad61a5b210))

* hotfix-ignore-reactions ([`f6e640d`](https://github.com/Sieboldianus/lbsntransform/commit/f6e640d2bb5f48c981f695dd24c01fd691a271ab))


## v0.1.517 (2018-12-18)

### Unknown

* Merged new features for Twitter filter ([`02c29a8`](https://github.com/Sieboldianus/lbsntransform/commit/02c29a8ac086ff78ba658fe4c8ed174377ea9616))

* Added several features for twitter input
- ignore input sources feature
- ignore non geotagged option
- ignore reactions for transfer ([`92d261a`](https://github.com/Sieboldianus/lbsntransform/commit/92d261a8309cf10a5c3477e409e72ca95e218dc2))

* Added pg application name reporting ([`5214cc7`](https://github.com/Sieboldianus/lbsntransform/commit/5214cc72de2f41b2b64adcda7e966e101fa8c2da))


## v0.1.516 (2018-12-10)

### Unknown

* Fixed setup.py to include package data; increase version ([`3590c56`](https://github.com/Sieboldianus/lbsntransform/commit/3590c56fede48da4ba5be4d06cdcfb9953bd7483))


## v0.1.515 (2018-12-06)

### Unknown

* Increase Minor Version Hotfix ([`9b0f0d3`](https://github.com/Sieboldianus/lbsntransform/commit/9b0f0d3a5ab99e6c5738a0cecf8f2a110074c5c6))

* include VERSION to your MANIFEST.in ([`3eced07`](https://github.com/Sieboldianus/lbsntransform/commit/3eced07f20bf128ace10ded42af4a5d7fd84f010))


## v0.1.514 (2018-12-06)

### Unknown

* Version 0.1.514 ([`aaad8e7`](https://github.com/Sieboldianus/lbsntransform/commit/aaad8e74de0166ed070846b3d94a953b1412efd9))

* Added version file and autoread scripts for Single-sourcing the package version
see [python.org packaging](https://packaging.python.org/guides/single-sourcing-package-version/) ([`4035b9f`](https://github.com/Sieboldianus/lbsntransform/commit/4035b9fc9eb0442859d5661f947aa1cce5a641dd))


## v0.1.513 (2018-12-06)

### Unknown

* Minor version increase ([`c1278b8`](https://github.com/Sieboldianus/lbsntransform/commit/c1278b8a29cafcfbb762bc99982065c1ec33046a))

* Minor load-data-fix ([`fc4c448`](https://github.com/Sieboldianus/lbsntransform/commit/fc4c448331dbaba726d077aa990df9860a5e374b))


## v0.1.512 (2018-12-05)

### Unknown

* Minor code optimization, tests ([`5aa9a1d`](https://github.com/Sieboldianus/lbsntransform/commit/5aa9a1dc3724af3397f0abf7923509a306ebca6c))

* Added classes to include in manifest.in instead of setup.py
don&#39;t use both! ([`0b73a5c`](https://github.com/Sieboldianus/lbsntransform/commit/0b73a5cac439a991fc2191a7d391f89ff42ebf63))


## v0.1.511 (2018-12-05)

### Unknown

* Fixed setup.py to include classes for pip install ([`439eeb2`](https://github.com/Sieboldianus/lbsntransform/commit/439eeb2094b124e1f6e65d572875957cce0682c1))

* Added new classes to _init_ ([`39beb4d`](https://github.com/Sieboldianus/lbsntransform/commit/39beb4dce1bf632543d451524635e19179c79930))


## v0.1.510 (2018-12-05)

### Unknown

* Increased version to 0.1.510, updated readme, prepared for pypi ([`606a2ea`](https://github.com/Sieboldianus/lbsntransform/commit/606a2ea96012025d38c5a303ab97c187a4ab1de4))

* Merge branch &#39;hot-fix-flickr&#39; into &#39;master&#39;

Hot Fix for Flickr mapping, tested

See merge request lbsn/lbsntransform!3 ([`b841817`](https://github.com/Sieboldianus/lbsntransform/commit/b841817a38493577d5885afefba91559ba42c296))

* Hot Fix for Flickr mapping, tested ([`1346179`](https://github.com/Sieboldianus/lbsntransform/commit/13461792392bcbff0cb82616e4e92a2c79e9bfcd))

* Merge Conflicts field mapping flickr ([`7467151`](https://github.com/Sieboldianus/lbsntransform/commit/7467151e5e0c750de915d9656badb24217504554))

* Merge branch &#39;flickr-mapping&#39; into &#39;master&#39;

Flickr mapping (tested function)

See merge request lbsn/lbsntransform!1 ([`3e6f6ea`](https://github.com/Sieboldianus/lbsntransform/commit/3e6f6ead8b01b13d89aebc05cbbc3e771a23a5a3))

* Flickr mapping (tested function) ([`d789978`](https://github.com/Sieboldianus/lbsntransform/commit/d7899785d99b82489ffb91b44c3f294976576424))

* Cleaned up Flickr Mapping, ready for master ([`186a832`](https://github.com/Sieboldianus/lbsntransform/commit/186a8328af8113121ffd8322bf6b354d970ff28b))

* Fixed some minor bugs after testing on lbsn_test ([`e7751d9`](https://github.com/Sieboldianus/lbsntransform/commit/e7751d95245d5664206f2625ac78bd20a94b1783))

* First stable Flickr mapping ([`ff61db4`](https://github.com/Sieboldianus/lbsntransform/commit/ff61db4ca59faa77335c9cd59ceb366abe31897b))

* Updated Flickr post mapping.
- also replaced line endings CRLF to LF only as to better cross os collaboration ([`5ec719d`](https://github.com/Sieboldianus/lbsntransform/commit/5ec719d5b1d1314a25207bc3e62573bfe226d8ae))

* Initial Flickr mapping structure ([`a1f6e54`](https://github.com/Sieboldianus/lbsntransform/commit/a1f6e546401e48e9632bd1330ce210d543bc617d))

* Initial Flickr Input ([`bd77cb0`](https://github.com/Sieboldianus/lbsntransform/commit/bd77cb09d2c0a1bfb4803502be212cb9da3796e5))

* Maintenance work and code style optimization ([`7fe87a3`](https://github.com/Sieboldianus/lbsntransform/commit/7fe87a3445f30978581cda239a1f02618f48d3d6))

* Maintenance work and code style optimization ([`a851b1a`](https://github.com/Sieboldianus/lbsntransform/commit/a851b1af5827530d7907572b42e837f6f0133780))

* Local input bug fix ([`d5e6f8c`](https://github.com/Sieboldianus/lbsntransform/commit/d5e6f8cf1184a2524c327917b53e2696667f4a1e))

* updated readme ([`9cb8adf`](https://github.com/Sieboldianus/lbsntransform/commit/9cb8adf975799d419daa17833d2764566c774734))

* Cleaned input args ([`4730eb7`](https://github.com/Sieboldianus/lbsntransform/commit/4730eb774d13971f399ae13495f126149c036000))


## v0.1.5 (2018-12-03)

### Unknown

* Increased version to 0.1.5 ([`8c7a407`](https://github.com/Sieboldianus/lbsntransform/commit/8c7a407af6e6b0654739ce5aa9bb030302150d3b))

* Fixed single file output bug ([`c170da5`](https://github.com/Sieboldianus/lbsntransform/commit/c170da502c49c8d1c6582163c06d86d2a417e451))

* Refactor CSV and LBSN db into separate classes
- formatted csv methods to pep guidelines
- added additional class for proto-lbsn-db mapping
- some additional cleanups ([`a431370`](https://github.com/Sieboldianus/lbsntransform/commit/a43137093a94acfc2c6c7a30148a16d020a6d760))

* updated backup gitignore ([`7a85383`](https://github.com/Sieboldianus/lbsntransform/commit/7a85383e6f048f183bc10fbc8617a8069735a5ff))

* gitignore fix for vs .sln ([`3424514`](https://github.com/Sieboldianus/lbsntransform/commit/34245146d4cfd93c28a6a0b8edc9da3f1d90c156))

* Added support for additional mapping modules (extend Flickr) ([`49972ab`](https://github.com/Sieboldianus/lbsntransform/commit/49972ab4d39272b1928d44329303b65726c9cb8c))

* Updated Timestamp to include native protobuf package; added lbsntransform to PyPi
- minor modifications to readme and setup.py ([`7fa200f`](https://github.com/Sieboldianus/lbsntransform/commit/7fa200f67407564590158c0181887a73a925b575))

* Updated readme ([`febf204`](https://github.com/Sieboldianus/lbsntransform/commit/febf204cbc37afbd5a822a8dcec6e399847ac2e7))

* Updated readme ([`51c38f0`](https://github.com/Sieboldianus/lbsntransform/commit/51c38f029759aca197fab9dcc4a62499ff36e0b7))

* Updated readme ([`40f891c`](https://github.com/Sieboldianus/lbsntransform/commit/40f891c7daa34d8dd24a0dd6779136bd57df1de5))

* Updated readme ([`024dcb6`](https://github.com/Sieboldianus/lbsntransform/commit/024dcb632630f7137750c65ffb9675fb2e0e7845))

* Updated readme ([`cdcd197`](https://github.com/Sieboldianus/lbsntransform/commit/cdcd197063f257a7050046cc250a3023e047891a))

* Updated readme ([`0775af3`](https://github.com/Sieboldianus/lbsntransform/commit/0775af3670edeaf514a5624358c771d7e5dc577c))

* Updated readme ([`50c067a`](https://github.com/Sieboldianus/lbsntransform/commit/50c067a34a7fa2e9cac51221aeea0d6e1190dc12))

* Updated readme ([`c063ab5`](https://github.com/Sieboldianus/lbsntransform/commit/c063ab557a077fc3a11ea03ee7d938e20fe20477))

* Updated readme ([`195419e`](https://github.com/Sieboldianus/lbsntransform/commit/195419ec2756a1c762eac878fd6dfa2898d44915))

* Updated readme ([`25b1679`](https://github.com/Sieboldianus/lbsntransform/commit/25b16799437c340ab6fa23492bfb4c477259fa43))

* Added License, cx_freeze setup and complete rewrite of README.md ([`cd2ee5d`](https://github.com/Sieboldianus/lbsntransform/commit/cd2ee5dc8b3412ae67113a0ad54c9fec26c6936a))


## v0.1.4 (2018-07-26)

### Unknown

* Merge branch &#39;master&#39; of gitlab.vgiscience.de:lbsn/lbsn-twitter-json-mapping ([`cb3e5f5`](https://github.com/Sieboldianus/lbsntransform/commit/cb3e5f5ae1d4173972c44cfe5f242408dad3b782))

* Remove remote VS ([`e75b81c`](https://github.com/Sieboldianus/lbsntransform/commit/e75b81cd6252e9de985bbda2a1e440c185d15260))

* Remove remote VS ([`722b4ea`](https://github.com/Sieboldianus/lbsntransform/commit/722b4ea53d931969d90c7cbc7fb236dbaae50dd1))

* Updated gitignore ([`c44825f`](https://github.com/Sieboldianus/lbsntransform/commit/c44825f00a7b5ba90fb0ecc957a9256efdaa4b2b))

* Updated naming structure to Pep 8 conventions ([`f066437`](https://github.com/Sieboldianus/lbsntransform/commit/f0664374caf2dd9b0d8bfbe3f4c093d037fbed19))

* Removed VS solution file ([`8335d4b`](https://github.com/Sieboldianus/lbsntransform/commit/8335d4bbe1180431d0f2cfee654a8b71fb0fe137))

* Added script execution function through __main__.py for main package ([`0dce759`](https://github.com/Sieboldianus/lbsntransform/commit/0dce7598da0a46c2f8eea2faa31e0ee36f00c661))

* Added script execution function through __main__.py for main package ([`c46068a`](https://github.com/Sieboldianus/lbsntransform/commit/c46068a9023963490a58e3f0b32dff719b95e47f))

* Merge branch &#39;master&#39; into refactor-structure ([`65fe4ee`](https://github.com/Sieboldianus/lbsntransform/commit/65fe4eea50ff6ab1207386a578fec66eaf3b0771))

* Added files to gitignore ([`a645946`](https://github.com/Sieboldianus/lbsntransform/commit/a645946b4f091540ac821051c3ea445a114db740))

* Added scripts to git ignore ([`64ea3a0`](https://github.com/Sieboldianus/lbsntransform/commit/64ea3a0cea49d5dc7d7193ce3e702aa7b586e13d))

* Moved closer to python structure convention ([`2478044`](https://github.com/Sieboldianus/lbsntransform/commit/247804463501c16ea4493cc8b833f5c2c274caf5))

* Started to refactor structure ([`ee15196`](https://github.com/Sieboldianus/lbsntransform/commit/ee1519662c105787d04bcec31bf635eee3c836f4))

* Moved Code Files in Subfolder according to Minimal Guide ([`a82ae46`](https://github.com/Sieboldianus/lbsntransform/commit/a82ae46c8f590a0ee2db5d5df403dce02e76b7b3))

* Updated formatting to python conventions ([`e15d2ed`](https://github.com/Sieboldianus/lbsntransform/commit/e15d2edd49940275e2f72cd179b07803cd08d822))

* Improved use of python code style conventions for main module ([`8d017c8`](https://github.com/Sieboldianus/lbsntransform/commit/8d017c816a8013a1f53a0ce4d36a329fd325f147))

* Added build/setup. Fixed loop in merge ([`c360ae6`](https://github.com/Sieboldianus/lbsntransform/commit/c360ae605b5e6976adacc966eac468e02ffe4da3))

* Removed files from git ([`5430048`](https://github.com/Sieboldianus/lbsntransform/commit/5430048e10dc1946972e9ecf247303bb8446279d))

* Removed files from git ([`422cda7`](https://github.com/Sieboldianus/lbsntransform/commit/422cda7fe697897a6f86048a801da7928f152fcf))

* updated git ignore ([`f46ecdf`](https://github.com/Sieboldianus/lbsntransform/commit/f46ecdfe256ae9ea05e1e69825e2c1f6e6554c45))

* Added setup.py, built test wheel ([`4233a90`](https://github.com/Sieboldianus/lbsntransform/commit/4233a90110219319c4c2f257027d206b3a127e84))

* Moved to Visual Studio for Dev; Added Files to gitignore ([`5e50a8b`](https://github.com/Sieboldianus/lbsntransform/commit/5e50a8b426f33fc5606ea35e8fe70293c8b88923))

* Added Split Output for large Input Files. Needs testing. ([`56164f2`](https://github.com/Sieboldianus/lbsntransform/commit/56164f21d67b17f9c2841a7ac32cedf39cf09779))

* Increased version from 0.1.3 to 0.1.4 ([`76832f9`](https://github.com/Sieboldianus/lbsntransform/commit/76832f916d8786e2688cd5570f9cb70013b3332f))

* Working Update of CSV Output/ Write to File ([`e67c152`](https://github.com/Sieboldianus/lbsntransform/commit/e67c152d3aef64f26a9cc6e9a31a8f1b03318ad6))

* Fixed Headers written bug ([`83a582f`](https://github.com/Sieboldianus/lbsntransform/commit/83a582ff385b3c3c75497ccc37433b74052c7fa9))

* Added sorting &amp; merging for output CSVs ([`bb9d6d8`](https://github.com/Sieboldianus/lbsntransform/commit/bb9d6d89f06b51b4aac00bd667b918ecc6075c80))

* Small refactoring for SQL inserts; fixed bug in transferlimit loop ([`6770f61`](https://github.com/Sieboldianus/lbsntransform/commit/6770f618582b0e73369b2919649b6649e73c4d6b))

* Significant refactoring to implement parallel CSV output for faster /Copy Import
- also refactored ugly select function and dict procedures, now procedural ([`13ae6ac`](https://github.com/Sieboldianus/lbsntransform/commit/13ae6ac88a515ba256aae9e9d831b7b80181b3c5))

* Added CSV Output for later COPY FROM file import ([`00482f7`](https://github.com/Sieboldianus/lbsntransform/commit/00482f7bace81babcef1fe0783fd8f6df0ca2313))

* Added missing 0 ([`f6570d8`](https://github.com/Sieboldianus/lbsntransform/commit/f6570d81e517d8fb9882167508b487af1ffc1978))

* No Transferlimit if transferlimit = 0 ([`06197dc`](https://github.com/Sieboldianus/lbsntransform/commit/06197dcaafcbb95bc76d834f4915072a6478eac3))

* Changes to submit routine for new lbsn structure ([`f515857`](https://github.com/Sieboldianus/lbsntransform/commit/f5158576b346074c53ab356c984ede0455707fe0))

* Added count affected monitoring ([`f1a8e99`](https://github.com/Sieboldianus/lbsntransform/commit/f1a8e99e624f67ab0e7547eb2b8985f0ee6f3e63))

* Fixed fieldMapping Greatest and mergeArray (P)SQLs ([`deeb854`](https://github.com/Sieboldianus/lbsntransform/commit/deeb854fd4ff849172f4904914eb98bec90d1387))

* Changed user submission to coalesce because of overwritten by NULL bug ([`4067ed6`](https://github.com/Sieboldianus/lbsntransform/commit/4067ed6d61d0c0a0dba5a16c4385619604468280))

* Added mapping of full relations (m-to-m relationships)
- for user_groups follows, user_groups_member, user_mentions, user_friend, user_connected ([`63ce830`](https://github.com/Sieboldianus/lbsntransform/commit/63ce830d0434ff765b4e3a9f5a812d9b83a82041))

* Added Relation-Structure to transfer script; Added friends &amp; follows mapping
- many-to-many relationships can now fully be mapped (e.g. isFriend, isFollwer etc.) ([`1ee9a26`](https://github.com/Sieboldianus/lbsntransform/commit/1ee9a264a7167a36b078b6627da3b3e75b347e75))

* Fixed memory leak; added memory_leak detection function
- see https://stackoverflow.com/questions/50984524/python-dict-switcher-results-in-memory-leak/50984854#50984854 ([`3cb36e2`](https://github.com/Sieboldianus/lbsntransform/commit/3cb36e21e826b3b31d8b66bb43de37737032dbeb))

* Fixed a bug that would result in empty object assigned to dict (Passing of Vars) ([`98a9af7`](https://github.com/Sieboldianus/lbsntransform/commit/98a9af799e58569b153111a70c3667c35cae495d))

* Tested live &amp; local Input and fixed several smaller bugs
included time monitoring class ([`1562954`](https://github.com/Sieboldianus/lbsntransform/commit/1562954d2abb8fd253b57d47d79a00c8579443c6))

* Added Geocoding Option for Text Location Strings ([`ae10cb8`](https://github.com/Sieboldianus/lbsntransform/commit/ae10cb87f511a07d8ebd6cecffe96b79894a943d))

* Fixed missing Language for user exception ([`573fb9a`](https://github.com/Sieboldianus/lbsntransform/commit/573fb9a64d91bf8789e7eb23405ae6d68444ea92))

* Fixed bug in Record Merge that would overwrite values with default ([`44c7897`](https://github.com/Sieboldianus/lbsntransform/commit/44c7897d2d0ce2c11df8a7acc11a0ff2485abcd3))

* Added User Groups Structure ([`9d86bc5`](https://github.com/Sieboldianus/lbsntransform/commit/9d86bc5513cbfd5c6ff54f2472859728eee429a5))

* Fixed Nul Error on prepare psycopg2 ([`e319d58`](https://github.com/Sieboldianus/lbsntransform/commit/e319d587492bc88a5c006be16fce18b6853ae137))

* Added Batching of Insertions for significant speed increase to output db ([`2d686a9`](https://github.com/Sieboldianus/lbsntransform/commit/2d686a9ffd68afe653970f8591da497aca85aa2d))

* Fixed bug in Exception Handling of Submit Routine ([`bb0e56f`](https://github.com/Sieboldianus/lbsntransform/commit/bb0e56f5fc6484679e9790edbf3557ef9bc43d2f))

* Removed comments ([`60f6918`](https://github.com/Sieboldianus/lbsntransform/commit/60f6918f2fa59a6640dd2d2b5f615c9e090092af))

* Removed comments ([`5256a91`](https://github.com/Sieboldianus/lbsntransform/commit/5256a9135c1e76fc9be03ff1143ab73d77ac3fd4))

* Improved handling of missing UserGuids for some Post ([`0b82afb`](https://github.com/Sieboldianus/lbsntransform/commit/0b82afbc27179c8ecb3d4651245b398351731bb9))

* Added Input and processing for stackedJson (no nesting) ([`3f3d6a6`](https://github.com/Sieboldianus/lbsntransform/commit/3f3d6a65d6f3ee754c82a65952c27ec1c0680910))

* Fixed bugs in lbsn_dbRetrieve due to CSV/JSON update ([`75b20f7`](https://github.com/Sieboldianus/lbsntransform/commit/75b20f7d72630f522323131ea998a58ffe649882))

* Bugfix for retweet parsing ([`206b65e`](https://github.com/Sieboldianus/lbsntransform/commit/206b65e12895580d594a392114b1a762b51d827b))

* Added option to read from local *.json/*.csv ([`fc5156a`](https://github.com/Sieboldianus/lbsntransform/commit/fc5156a4a90d0329d6a8d8fcf2e4286ba6cc4955))

* Improved reporting. Changed &#39;Reply&#39; to &#39;Comment&#39; ([`449ec50`](https://github.com/Sieboldianus/lbsntransform/commit/449ec50bf33abe2298c28b9c76d1123e5a96d63b))

* Improved DB Input and Output Loop procedure for increased speed
- less take on Output DB due to more processing in-memory ([`b914900`](https://github.com/Sieboldianus/lbsntransform/commit/b914900d4f480af3595b62cf026b4659f72e03dd))

* Moved config to separate file ([`56b810a`](https://github.com/Sieboldianus/lbsntransform/commit/56b810a54709f9741dd93ff6495bc5b3a88ea9c0))

* Minor refactoring of __main__ ([`3f9d78c`](https://github.com/Sieboldianus/lbsntransform/commit/3f9d78c6af4442ddd939e8a117c7017cc47286f1))

* Removed useless finished from break loop ([`7d3347d`](https://github.com/Sieboldianus/lbsntransform/commit/7d3347d18d4b835dbefec0467076441028694379))

* Removed duplicate = ([`465140c`](https://github.com/Sieboldianus/lbsntransform/commit/465140ca9ab504079fb1e4ff351d9047a5be6933))

* Bugfix for assignment of place names and place name alternatives ([`3bedb7c`](https://github.com/Sieboldianus/lbsntransform/commit/3bedb7c8f942fcdc20686f8b250762e104c5f818))

* Added missing conn.rollback() on exception ([`bd7c22a`](https://github.com/Sieboldianus/lbsntransform/commit/bd7c22a4f3a7dc89a8bbda4f7b82448a2c7ea3f2))

* Added function to automatically add languages on insertion exception ([`e19e254`](https://github.com/Sieboldianus/lbsntransform/commit/e19e254b2dffa6c158f84ab794cd86fc28d19b83))

* Significant refactoring of classes.fieldMapping. Mapping of tweet to lbsn Structure should be more logical now ([`c252419`](https://github.com/Sieboldianus/lbsntransform/commit/c252419078d9b9ec72ead47b9cf234d64d325138))

* Removed debug comments ([`d78f571`](https://github.com/Sieboldianus/lbsntransform/commit/d78f571441320e257d0372d99fb5ea6ab46d8f00))

* Improved Reporting and DB Loop procedures ([`91a8e2e`](https://github.com/Sieboldianus/lbsntransform/commit/91a8e2e8cf2c457cce72b0f5eee0b3915be3b95c))

* Added transfer functions for user, post and post_reaction ([`5fd7d4f`](https://github.com/Sieboldianus/lbsntransform/commit/5fd7d4f6ca2636b515952fc70b4a3c7f00c2775f))

* Added Submit Functions for Place and City ([`df119bc`](https://github.com/Sieboldianus/lbsntransform/commit/df119bcbd260d0dfae45179bf1870c62987cbbb8))

* Added enhanced Array_Merge for name_alternatives column; added args for startInputID to endInputID ([`e3cb761`](https://github.com/Sieboldianus/lbsntransform/commit/e3cb76167965ee0e4ab42676f8a5fd270289b08a))

* Added bytefiles to git ignore ([`5d40b08`](https://github.com/Sieboldianus/lbsntransform/commit/5d40b08cb0a7ee6b2aa27e0766555c005054646c))

* Removed bytecode from git ([`7e1b1ce`](https://github.com/Sieboldianus/lbsntransform/commit/7e1b1ce9c0cc693697d48a9195045fcae2aeda90))

* Added Github boilerplate gitignore ([`45a2c4c`](https://github.com/Sieboldianus/lbsntransform/commit/45a2c4c87b50b6ba3861c866f2bc4e9ede9fee2a))

* Added submit entry function for lbsnCountry; tested on lbsn_test ([`42561bb`](https://github.com/Sieboldianus/lbsntransform/commit/42561bb727da7813feb54e4912d7f1f0436312e4))

* Added Author, Version, License; added submitData class ([`395c2b0`](https://github.com/Sieboldianus/lbsntransform/commit/395c2b023ca827bb4fa9faa48790d47729251a71))

* Cleaned up comments ([`fbc6279`](https://github.com/Sieboldianus/lbsntransform/commit/fbc6279d8ba2491386ca31caed9585a4640b4307))

* reset default values for args ([`c885bc0`](https://github.com/Sieboldianus/lbsntransform/commit/c885bc02557dc7ffb24d69a9861cbc25faff3d33))

* Added output pw to example config; Added DBRowNumber reporting in __main__ ([`ead1cbd`](https://github.com/Sieboldianus/lbsntransform/commit/ead1cbd7054c1ccbcebca1fe5e6e288074b00801))

* Fixed missing Country, Place and City refs in lbsnPost Mapping ([`85c44d4`](https://github.com/Sieboldianus/lbsntransform/commit/85c44d4060f0b0a2498245aa9e5567bc95759852))

* Fixed bug in name_alternatives assignment duplicating main &#39;name&#39; for places ([`ff1371b`](https://github.com/Sieboldianus/lbsntransform/commit/ff1371b13bf3179d1076cfb16295c929b82a3ed7))

* Small refactoring ([`90095a7`](https://github.com/Sieboldianus/lbsntransform/commit/90095a71f3c5475fadacbc3c9bf86cd763da97d5))

* Added basic deep comüpare routine for 2 comparing and merging all values of all fields of two records ([`98c8e99`](https://github.com/Sieboldianus/lbsntransform/commit/98c8e9994f9832cc57d025fed685ec5f38d4a89d))

* Better Count of records, fixed referencing issues ([`bcfd1de`](https://github.com/Sieboldianus/lbsntransform/commit/bcfd1dea45d18449bb88925439d33b481cbae33b))

* BugFix in DB Loop Records ([`81dcc58`](https://github.com/Sieboldianus/lbsntransform/commit/81dcc58c7072fb21b361991ac1c3bb9da1bd1d12))

* Added Composite Structure for storing individual records ([`c561d01`](https://github.com/Sieboldianus/lbsntransform/commit/c561d01182d8976a7868b658a868dd1cc7ef9cc1))

* completed mapping of twitter json to protobuf lbsn structure ([`2e15c83`](https://github.com/Sieboldianus/lbsntransform/commit/2e15c839993365855b51c036dd65b3e2a32aada3))

* Readme formatting ([`dcadc3d`](https://github.com/Sieboldianus/lbsntransform/commit/dcadc3db7ff7190897be321567f2e30c3fe1167a))

* Readme formatting ([`2d19778`](https://github.com/Sieboldianus/lbsntransform/commit/2d19778b791111457e3451676e80b607f8873d90))

* Readme formatting ([`24090a0`](https://github.com/Sieboldianus/lbsntransform/commit/24090a04567528ef61ff5028f3b02465c1bec001))

* First version of complete Twitter Tweet mapping to lbsn-protobuf ([`500d751`](https://github.com/Sieboldianus/lbsntransform/commit/500d7511d3c0b699c4631ce88e0f4d643034fe1c))

* Added missing linebreaks in README ([`f2b1079`](https://github.com/Sieboldianus/lbsntransform/commit/f2b107901a17e8eea1962170a493e0eded124c4d))

* Added missing linebreaks in README ([`6920180`](https://github.com/Sieboldianus/lbsntransform/commit/6920180a03c1995924a5381b64a1a148bcbb2a00))

* Added missing linebreaks in README ([`6da73be`](https://github.com/Sieboldianus/lbsntransform/commit/6da73bea5452bb29513eb0e74093c5141a95dedd))

* Added missing linebreaks in README ([`0c1a786`](https://github.com/Sieboldianus/lbsntransform/commit/0c1a78617b4547f6315a9b1d9a129f3ae8e68402))

* Added README ([`96695a9`](https://github.com/Sieboldianus/lbsntransform/commit/96695a995cc115ac1e7e2231ef5ae74267b8a0e8))

* Added gitignore; implemented lbsn protobuf structure; restructured code to protobuf defenitions  - everything up to postReaction done ([`2bb2c2d`](https://github.com/Sieboldianus/lbsntransform/commit/2bb2c2d68c5209a01c70df24a73e0b19f1ad91e7))

* Added LBSN ProtoBuf Structure 0.1.5 ([`25bbb75`](https://github.com/Sieboldianus/lbsntransform/commit/25bbb751ea50c3487dd0bf33958ccf2bcb7e15f3))

* Initial Commit ([`9c792fb`](https://github.com/Sieboldianus/lbsntransform/commit/9c792fb6de3233fd2aef0dd45a86c4c903a5e3d5))
