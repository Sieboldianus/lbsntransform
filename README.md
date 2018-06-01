## LBSN Data Structure Concept: Twitter-json_protobuf_mapping

This tool will read JSON strings from a Postgres Database or local folder* and map the Twitter Endpoints to our common [LBSN Data Structure](https://gitlab.vgiscience.de/lbsn/concept) in ProtoBuf.

^* Not currently implemented

### Quick Start

1. Create a local clone of this repository: `git clone git@gitlab.vgiscience.de:lbsn/lbsn-twitter-json-mapping.git`
2. Download current version of Python compiled ProtoBuf folder "[lbsnstructure](https://gitlab.vgiscience.de/lbsn/concept/tree/master/examples/python)" and place in your local copy root folder
3. Edit `/config/config.py`, or optionally provide the following command line args:

    -pO # passwordOutput (this is the password for the PostGres database where output will be send to; if 0, user will be asked)  
    -uO # usernameOutput (this is the username for the PostGres database where output will be send to; example: "someuser")  
    -aO # serveradressOutput (the IP Adress of the PostGres database where output will be send to, example: 111.79.10.12)  
    -nO # dbnameOutput (the database name of the PostGres database where output will be send to, example: "lbsn_test")  
    -pI # passwordInput (same as above, just where the data is coming from)  
    -uI # usernameInput  
    -aI # serveradressInput  
    -nI # dbnameInput  
    -t # transferlimit (stop script after x records, example: 50)  
    -tR # transferReactions (choose whether to process original posts only [`0`] or also include reactions to these posts such as retweets [`1`])  
    -tG # transferNotGeotagged (choose whether to limit processing to geotagged posts only [`0`] or also include non-geotagged posts [`1`])  
