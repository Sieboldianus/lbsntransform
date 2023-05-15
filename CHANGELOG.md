# Changelog

<!--next-version-placeholder-->

## v0.25.0 (2023-05-15)
### Feature
* Add mapping for Reddit comments and submissions ([`a665e9d`](https://github.com/Sieboldianus/lbsntransform/commit/a665e9da27b647c9e685f81b7b13a4f488268598))
* Add new topic_group and post_downvotes attribute ([`12c6bbb`](https://github.com/Sieboldianus/lbsntransform/commit/12c6bbbf1db520fe456ffa04bc657111785230cb))
* Allow handing pre-defined BaseConfig to main() ([`14549d9`](https://github.com/Sieboldianus/lbsntransform/commit/14549d954f2102cbc7a5d4bcb9471551600aeec9))

### Fix
* Report package version without package name ([`94081e0`](https://github.com/Sieboldianus/lbsntransform/commit/94081e0e0bc92cdd79edfb077f5c79ff0b7861f9))

## v0.24.2 (2023-05-09)
### Fix
* Update yml dependencies to use version range for protobuf, too ([`bfad7b2`](https://github.com/Sieboldianus/lbsntransform/commit/bfad7b26d2537a6855246f02885dd9b592938121))
* Migrate from setup.cfg to pyproject.toml ([`7ee7598`](https://github.com/Sieboldianus/lbsntransform/commit/7ee759805566b58f7ec295b5ad2f70fc03a5dfd2))

### Documentation
* Update to reflect pyproject.toml only based setup ([`6bce8d9`](https://github.com/Sieboldianus/lbsntransform/commit/6bce8d9e4784709ab25d6ea6944edfd89edea880))
* Fix formatting in cli-commands page ([`c482347`](https://github.com/Sieboldianus/lbsntransform/commit/c4823478aa9c7a2574fd06a26e57d6739de17542))

## v0.24.1 (2023-05-05)
### Feature
* Migrate from setup.py to setup.cfg & pyproject.toml ([`7de0de0`](https://github.com/Sieboldianus/lbsntransform/commit/7de0de0480fb1b9956de5cc0c34c52536627b892))

### Documentation
* Add information regarding semantic release versioning ([`eb667d4`](https://github.com/Sieboldianus/lbsntransform/commit/eb667d4d866826ed34bbda174bb4f8f9034e33bb))
* Update installation instructions based on new dependencies and deprecated setup.py ([`416c869`](https://github.com/Sieboldianus/lbsntransform/commit/416c869d41dace88c12f8e6270644f470d02332e))
* Add a short description of the file structure and layout ([`d56041d`](https://github.com/Sieboldianus/lbsntransform/commit/d56041d16c06b6389b67bf3aaad7e98dae43978f))

## v0.23.0 (2022-11-23)
### Feature
* Add experimental temporal._month_hashtag_latlng base processing ([`60da223`](https://github.com/Sieboldianus/lbsntransform/commit/60da223bdaa56f714b4d6fb8889ad879183790b9))

### Fix
* NLTK stopwords not available notice ([`c395bcb`](https://github.com/Sieboldianus/lbsntransform/commit/c395bcb1404cc135a85f1e65efd29af57efed4d2))

## v0.22.1 (2022-11-22)
### Fix
* EMOJI_UNICODE deprecated in emoji>=2.0.0 ([`3097a42`](https://github.com/Sieboldianus/lbsntransform/commit/3097a42df36e245234562582c97b6b93f655cccd))
* --skip_until_file not implemented ([`18e7665`](https://github.com/Sieboldianus/lbsntransform/commit/18e7665fed14a027889e93f59f4e022702a86500))
* Fix TypeError NoneType for skipped_geo reporting ([`fe67231`](https://github.com/Sieboldianus/lbsntransform/commit/fe6723137a7ac6c1170acea55c1353698058d3b0))
* Catch empty values in lbsn database record arrays ([`6ad2d82`](https://github.com/Sieboldianus/lbsntransform/commit/6ad2d82876e75533d8fd3ec072e03775311383e0))

### Documentation
* Fix typo ([`7e43ef4`](https://github.com/Sieboldianus/lbsntransform/commit/7e43ef43bbca4ec4452d04ce7afcff44149fab52))
* Fix typo ([`05c623c`](https://github.com/Sieboldianus/lbsntransform/commit/05c623c213faee91dc0771e823b00166ba8d1a6b))
* Fix typo in --commit_volume cli docs ([`70d96b9`](https://github.com/Sieboldianus/lbsntransform/commit/70d96b90a6a5df5cfff5c2e73375b5a1e490f78a))
* Better explain the use of ([`e43afdd`](https://github.com/Sieboldianus/lbsntransform/commit/e43afdd8e359143cdb58cad3c5d00019cf237fa9))
* Clarify to use all lbsn objects by default when mapping from lbsn raw ([`202fd75`](https://github.com/Sieboldianus/lbsntransform/commit/202fd759e9127d2761ff189623b5c8d9d9ad8c6e))
* Fix internal link ([`67f4c90`](https://github.com/Sieboldianus/lbsntransform/commit/67f4c90ab77e780b60018483a8ec9891fd08cab0))
* Improve description of --include_lbsn_bases and --commit_volume args ([`b7697a3`](https://github.com/Sieboldianus/lbsntransform/commit/b7697a315c01eb09513cc75048fc5151cdfed91f))
* Add header information on command line interface page ([`9602c47`](https://github.com/Sieboldianus/lbsntransform/commit/9602c47dad3eddb5b32941619d124e794406be6b))
* Add changelog to documentation ([`766a40d`](https://github.com/Sieboldianus/lbsntransform/commit/766a40d8335f7d7f32fa801f4b8ef75d43e6401c))

### Performance
* Clear key hashes on finalize_output() ([`864336d`](https://github.com/Sieboldianus/lbsntransform/commit/864336deee218c48602d17a20586ad285e300482))

## v0.22.0 (2022-04-08)
### Feature
* Allow --commit_volume to be overriden ([`50c4bf8`](https://github.com/Sieboldianus/lbsntransform/commit/50c4bf849dc453ccad778f5735a19c8a00d068cf))

### Fix
* Skip all base records with any empty key ([`e3caac1`](https://github.com/Sieboldianus/lbsntransform/commit/e3caac1437a4c1ef95ef14ad2be5488eb9c438b2))
* Skip empty keys for temporal hll structures ([`263774c`](https://github.com/Sieboldianus/lbsntransform/commit/263774c3f815b2bc66dc54e8f8d780400eb512f3))
* Compatibility for 'carousel' types from previous lbsnstructure ([`caf21c3`](https://github.com/Sieboldianus/lbsntransform/commit/caf21c3af7882beb70525008a016ccb563dd4357))

### Documentation
* Fix typo ([`4034867`](https://github.com/Sieboldianus/lbsntransform/commit/4034867ef09d357b730b00b8ea2db84abbad4a17))
* Add internal links to Use Cases ([`da93d5c`](https://github.com/Sieboldianus/lbsntransform/commit/da93d5c053b94a16a76803abde486e36e95d15fa))
* Add twitterparser example to use lbsntransform as a package ([`2a68f08`](https://github.com/Sieboldianus/lbsntransform/commit/2a68f086ebfdf8d64d15e6072b4c1a66249539c4))

## v0.21.3 (2022-03-18)
### Fix
* Pin google.protobuf to latest release 3.19.4 or earlier ([`f591487`](https://github.com/Sieboldianus/lbsntransform/commit/f591487a8d4c3fb71040a26caba2267049f1b657))

### Documentation
* Add note to activate optional nltk stopwords filter feature ([`015511e`](https://github.com/Sieboldianus/lbsntransform/commit/015511e27863b1b2f63176c498fc8b85f2721707))
* Deprecate cx_freeze setup ([`4700821`](https://github.com/Sieboldianus/lbsntransform/commit/4700821a3e4ca1d107e66fc2cc78b5a2e1ce4ea7))

## v0.21.2 (2022-03-18)
### Documentation
* Add hint towards Linux installation ([`ce2c75b`](https://github.com/Sieboldianus/lbsntransform/commit/ce2c75b68912a2485ae2ef195a7e4bd8dc4137d8))

## v0.21.1 (2022-03-17)
### Fix
* ScalarMapContainer not found in protobuf dependency (Windows only) ([`7d469f5`](https://github.com/Sieboldianus/lbsntransform/commit/7d469f5fa2e2ec93a0f02d5ae0c08384cf5c3ec0))
* Deactivate currently not supported CSV output ([`92f887d`](https://github.com/Sieboldianus/lbsntransform/commit/92f887d2691e32efe0378471f81862a0f6877c5d))

## v0.21.0 (2022-03-15)
### Feature
* Allow lbsntransform args to be predefined by another package ([`c587bbf`](https://github.com/Sieboldianus/lbsntransform/commit/c587bbf3f0f85abcf55e5b193ba947ad204d0914))

### Documentation
* Remove duplicate mappings_path from example ([`854aad5`](https://github.com/Sieboldianus/lbsntransform/commit/854aad5df685b71d7a72555e77231c545f2f608a))
* Fix internal links in Use Cases ([`61f772a`](https://github.com/Sieboldianus/lbsntransform/commit/61f772aef4f9dbe837c9d99906bbc004d242bf1a))

## v0.20.0 (2021-05-11)


## v0.19.0 (2021-05-11)
### Feature
* Add _month_latlng and _month_hashtag composite bases ([`71bbc22`](https://github.com/Sieboldianus/lbsntransform/commit/71bbc222924866a956964326a503ad2408aa3c0a))

## v0.18.3 (2021-05-05)
### Fix
* Csv.reader bug that got introduced in #2a79f01c ([`49243c5`](https://github.com/Sieboldianus/lbsntransform/commit/49243c5d663a76d6c8abcc550f113b09cd909bd0))

## v0.18.2 (2021-04-26)
### Fix
* On empty hmac, do not override if crypt.salt is set in hll worker db ([`24f0a4d`](https://github.com/Sieboldianus/lbsntransform/commit/24f0a4d535087697e70fe6bd535f77b9e1fb39bb))

### Documentation
* Improve description on how hmac defaults are used ([`aa5e265`](https://github.com/Sieboldianus/lbsntransform/commit/aa5e2651376efbfc3c9b74504f984b4fd6e75cd8))
* Fix badge links not updating on GH ([`8a425ed`](https://github.com/Sieboldianus/lbsntransform/commit/8a425ed986d489791374c7db6e58152a5a31f007))

## v0.18.1 (2021-04-19)
### Fix
* Error on empty HMAC ([`8d29832`](https://github.com/Sieboldianus/lbsntransform/commit/8d2983204d2496e979c71b39655b66bd512c3d4b))
* Grapheme clusters not found in newest emoji.UNICODE_EMOJI (emoji >= v.1.0.1) ([`cfd6f28`](https://github.com/Sieboldianus/lbsntransform/commit/cfd6f28684c6c56d4a54113fa712f285810289e5))

### Documentation
* Fix docstring typo ([`7d13423`](https://github.com/Sieboldianus/lbsntransform/commit/7d13423877622306fe39208de1d0b518b9538a77))

## v0.18.0 (2021-04-16)
### Feature
* Add function to extract @-Mentions from string ([`714d5c9`](https://github.com/Sieboldianus/lbsntransform/commit/714d5c9a6b4c1d17805d88232ca8138cd627e18f))
* Add option to switch to csv.DictReader() ([`2a79f01`](https://github.com/Sieboldianus/lbsntransform/commit/2a79f01cf259a7f2d74763d7adbed8dd59f65488))

### Documentation
* Improve description of --transfer_count ([`9847f5e`](https://github.com/Sieboldianus/lbsntransform/commit/9847f5e485e36bcab7ff56261277a514573be01c))

## v0.17.0 (2021-04-15)
### Feature
* Properly intergrate hmac hashing and warn user on empty key ([`4cecd96`](https://github.com/Sieboldianus/lbsntransform/commit/4cecd961a79d8e14e047b59eab11ce2498bf02ff))

### Documentation
* Fix list formatting ([`2751d74`](https://github.com/Sieboldianus/lbsntransform/commit/2751d742480a60f09d3e90e0387144743678b4eb))
* Fix typo ([`e000386`](https://github.com/Sieboldianus/lbsntransform/commit/e000386a9899b7c8c732282fb54331d8efbaf18b))
* Update Windows install instructions ([`9d0cb6e`](https://github.com/Sieboldianus/lbsntransform/commit/9d0cb6e393452d4e4e637a20fefd0b0ece1c1fea))
* Fix api link ([`b31b1ce`](https://github.com/Sieboldianus/lbsntransform/commit/b31b1ce2997aa45f3b1bebcc0af7312c57e560d1))
* Fix api link ([`1745f39`](https://github.com/Sieboldianus/lbsntransform/commit/1745f3942b737a86af0c9c666754692972431642))
* Add last git revision date to pages ([`b254df7`](https://github.com/Sieboldianus/lbsntransform/commit/b254df7cc4bf0aa029a22c19e050a99a961cca8d))

## v0.16.1 (2021-03-13)
### Documentation
* Fix Readme image link on pypi ([`ec352ca`](https://github.com/Sieboldianus/lbsntransform/commit/ec352cad0d9ded60b6dc719e6c19cbb6787519de))
* Major overhaul of CLI argument formatting ([`d12b4c1`](https://github.com/Sieboldianus/lbsntransform/commit/d12b4c1056b0fd496ed1c907a51321870f17927b))
* Improve formatting ([`c766d8e`](https://github.com/Sieboldianus/lbsntransform/commit/c766d8ed9a95d1247f26fb55bf97294ae705fbf0))
* Add docker mount note ([`dcd98a2`](https://github.com/Sieboldianus/lbsntransform/commit/dcd98a225df5cb19a6940d63d7916d91464b73ed))
* Add note towards Docker input from bind mounts ([`a1e1564`](https://github.com/Sieboldianus/lbsntransform/commit/a1e156484832945bd30e0544849027bdbd851ef1))
* Fix formatting issue in --override_lbsn_query_schema ([`ac26a2f`](https://github.com/Sieboldianus/lbsntransform/commit/ac26a2fff373261996b2662c47d653d58393ff8b))
* Fix typo ([`42fe31f`](https://github.com/Sieboldianus/lbsntransform/commit/42fe31ff43bfb2210a28b6d669678dd2631504ab))
* Add example to read from live lbsn db and to live hll db ([`b07a7c2`](https://github.com/Sieboldianus/lbsntransform/commit/b07a7c2e12e83a7f7398284a90f94fcd31456e1e))
* Correct order of --editable --no-deps for quirky pip ([`a768da1`](https://github.com/Sieboldianus/lbsntransform/commit/a768da14edc2b82a916e9e844501456a8cabefdb))

## v0.16.0 (2021-01-14)
### Feature
* Add --dry-run option ([`335631b`](https://github.com/Sieboldianus/lbsntransform/commit/335631b0b2a49eb18a9e25c852a6cca70d8ea9b1))

### Fix
* Disable CSV output until further notice ([`2014ce5`](https://github.com/Sieboldianus/lbsntransform/commit/2014ce5ac5e18aadb2bacdde62b7b6e954b217b9))

### Documentation
* Update linux install command ([`bc35783`](https://github.com/Sieboldianus/lbsntransform/commit/bc35783d7d9c352dd4c83a5acd1220533c9d9325))
* Update and cleanup Readme ([`f16cf2c`](https://github.com/Sieboldianus/lbsntransform/commit/f16cf2c15fc5d841e47fa80308d5d360d4aa11c0))
* Re-order recommended pip setup instructions ([`19e4575`](https://github.com/Sieboldianus/lbsntransform/commit/19e45759233d6b2ffc788d21e879bcf47f768358))

## v0.15.0 (2021-01-09)
### Feature
* Add method for hashtag extraction from string ([`134119c`](https://github.com/Sieboldianus/lbsntransform/commit/134119c2c774ea5b952bea2c52d8d49b5bd425f4))
* Dynamic load of mapping modules ([`09de72f`](https://github.com/Sieboldianus/lbsntransform/commit/09de72f23b5465e5928267d118c132607f5c9a74))

### Fix
* Improved exception reporting for malformed records ([`b7b83e2`](https://github.com/Sieboldianus/lbsntransform/commit/b7b83e2bfb96aa179ba791186623aaaf75b026db))

## v0.14.1 (2021-01-06)
### Fix
* Catch any geos.WKTReader() exceptions ([`14f7721`](https://github.com/Sieboldianus/lbsntransform/commit/14f7721902cd8a42304f6a80ff6e8d53263684a1))
* Windows lbsntransform.tools module not found. ([`1643112`](https://github.com/Sieboldianus/lbsntransform/commit/1643112ae7662274a408bf873754e58b14273395))

### Documentation
* Fix admonition formatting ([`c33b8c1`](https://github.com/Sieboldianus/lbsntransform/commit/c33b8c19569c6916ec17c603d7ac423e2301780d))
* Update conda install instructions ([`4f0f96b`](https://github.com/Sieboldianus/lbsntransform/commit/4f0f96b421efa606a1c02f86be9243d32093df8a))
* Fix links and rehrase sections ([`76875bf`](https://github.com/Sieboldianus/lbsntransform/commit/76875bf497c97fc154facb692e954dbe2e5f16ef))
