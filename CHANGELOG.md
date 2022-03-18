# Changelog

<!--next-version-placeholder-->

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
