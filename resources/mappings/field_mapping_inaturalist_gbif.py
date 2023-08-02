# -*- coding: utf-8 -*-

"""
Module for mapping iNaturalist gbif occurences to common LBSN Structure.

Notes:
- this is the mapping for "research"-grade iNaturalist data, submitted to gbif,
  and follows gbif simple [1] structure
- this mapping must be used with `--use_csv_dictreader` lbsntransform cli

[1]: https://www.gbif.org/data-quality-requirements-occurrences
"""


import logging
import hashlib
from typing import Optional, Dict, Tuple
from decimal import Decimal
from datetime import datetime

# pylint: disable=no-member
import lbsnstructure as lbsn

from lbsntransform.tools.helper_functions import HelperFunctions as HF

MAPPING_ID: int = 231
TIME_FORMAT: str = "%Y-%m-%dT%H:%M:%S"  # gbif time format used
# taxonomy-emoji mapping defined below, for experimental latin species mapping
# to known emoji
TAX_SPECIES = {
    "Canis familiaris": ("Dog", "🐕"),
    "Gallus domesticus": ("Chicken", "🐓"),
    "Trifolium repens": ("Clover", "🍀"),
    "Oryza sativa": ("Rice", "🌾"),
    "Helianthus annuus": ("Sunflower", "🌻"),
    "Rosa gallica": ("Rose", "🌹"),
    "Rosa × alba": ("Rose", "🌹"),
    "Paeonia broteri": ("Rose", "🌹"),
    "Pavo cristatus": ("Peafowl", "🦚"),
    "Pavo muticus": ("Peafowl", "🦚"),
    "Afropavo congensis": ("Peafowl", "🦚"),
    "Raphus cucullatus": ("Dodo", "🦤"),
    "Bos taurus": ("Cow", "🐄"),
    "Bubalus bubalis": ("water buffalo", "🐃"),
    "Panthera tigris": ("Tiger", "🐅"),
    "Panthera pardus": ("Leopard", "🐅"),
    "Felis catus": ("Cat", "🐈"),
    "Equus ferus": ("Horse", "🐎"),
    "Equus africanus": ("Donkey", "🫏"),
    "Ovis aries": ("Sheep", "🐑"),
    "Capra hircus": ("Goat", "🐐"),
    "Sus domesticus": ("Pig", "🐖"),
    "Sus scrofa": ("Boar", "🐗"),
    "Camelus dromedarius": ("Dromedary camel", "🐪"),
    "Camelus bactrianus": ("Bactrian camel", "🐫"),
    "Panthera leo": ("Lion", "🦁"),
    "Hippotigris zebra": ("Zebra", "🦓"),
    "Osphranter antilopinus": ("kangaroo", "🦘"),
    "Osphranter rufus": ("kangaroo", "🦘"),
    "Solanum lycopersicum": ("tomato", "🍅"),
    "Vitis vinifera": ("Grapes", "🍇"),
    "Cucumis melo": ("Melon", "🍉"),
    "Citrus × sinensis": ("Orange", "🍊"),
    "Citrus × limon": ("Lemon", "🍋"),
    "Ananas comosus": ("Pineapple", "🍍"),
    "Malus domestica": ("Apple", "🍎"),
    "Prunus persica": ("Peach", "🍑"),
    "Prunus avium": ("Cherry", "🍒"),
    "Cocos nucifera": ("Coconut", "🥥"),
    "Mangifera indica": ("Mango", "🥭"),
    "Olea europaea": ("Olive", "🫒"),
    "Solanum melongena": ("Eggplant", "🍆"),
    "Persea americana": ("Avocado", "🥑"),
    "Cucumis sativus": ("Cucumber", "🥒"),
    "Solanum tuberosum": ("Potato", "🥔"),
    "Daucus carota": ("Carrot", "🥕"),
    "Arachis hypogaea": ("Peanut", "🥜"),
    "Brassica oleracea ": ("Broccoli", "🥦"),
    "Spinacia oleracea": ("Leafy Green/Spinach", "🥬"),
    "Allium sativum": ("Garlic", "🧄"),
    "Allium cepa": ("Onion", "🧅"),
    "Capsicum annuum": ("Bell Pepper", "🫑"),
    "Palaemon serratus": ("Shrimp", "🦐"),
    "Nelumbo nucifera": ("Lotus", "🪷"),
    "Zingiber officinale": ("Ginger", "🫚"),
}
TAX_GENUS = {
    "Rattus": ("Rat", "🐀"),
    "Mus": ("Mouse", "🐁"),
    "Canis": ("wolf", "🐺"),
    "Oxalis": ("shamrock", "☘"),
    "Gymnosperma": ("Conifers", "🌲"),
    "Tulipa": ("Tulip", "🌷"),
    "Meleagris": ("Turkey", "🦃"),
    "Cygnus": ("Swan", "🦢"),
    "Ailuropoda": ("Panda", "🐼"),
    "Lycalopex": ("Fox", "🦊"),
    "Vulpes": ("Fox", "🦊"),
    "Macropus": ("kangaroo", "🦘"),
    "Lama": ("Lama", "🦙"),
    "Procyon": ("Raccoon", "🦝"),
    "Meles": ("Badger", "🦡"),
    "Arctonyx": ("Badger", "🦡"),
    "Mellivora": ("Badger", "🦡"),
    "Melogale": ("Badger", "🦡"),
    "Mydaus": ("Badger", "🦡"),
    "Taxidea": ("Badger", "🦡"),
    "Mammuthus": ("Mammoth", "🦣"),
    "Aonyx": ("Otter", "🦦"),
    "Enhydra": ("Otter", "🦦"),
    "Hydrictis": ("Otter", "🦦"),
    "Lontra": ("Otter", "🦦"),
    "Lutra": ("Otter", "🦦"),
    "Lutrogale": ("Otter", "🦦"),
    "Pteronura": ("Otter", "🦦"),
    "Pongo": ("Orangutan", "🦧"),
    "Gorilla": ("Gorilla", "🦍"),
    "Homo": ("Hominoids", "🧍"),
    "Castor": ("Beaver", "🦫"),
    "Bison": ("Bison", "🦬"),
    "Hibiscus": ("Hibiscus", "🌺"),
    "Prunus": ("Cherry", "🌸"),
    "Acer": ("Maple", "🍁"),
    "Musa": ("Banana", "🍌"),
    "Pyrus": ("Pear", "🍐"),
    "Fragaria": ("Strawberry ", "🍓"),
    "Actinidia": ("Kiwi ", "🥝"),
    "Vaccinium": ("(Blue)berries", "🫐"),
    "Castanea": ("Chestnut", "🌰"),
    "Capsicum": ("Pepper", "🌶️"),
    "Zea": ("Corn", "🌽"),
    "Phaseolus": ("Bean", "🫘"),
    "Hyacinthus": ("Hyacinth", "🪻"),
    "Alnus": ("Deciduous", "🌳"),
    "Betula": ("Deciduous", "🌳"),
    "Carpinus": ("Deciduous", "🌳"),
    "Crataegus": ("Deciduous", "🌳"),
    "Fagus": ("Deciduous", "🌳"),
    "Fraxinus": ("Deciduous", "🌳"),
    "Ilex": ("Deciduous", "🌳"),
    "Populus": ("Deciduous", "🌳"),
    "Quercus": ("Deciduous", "🌳"),
    "Salix": ("Deciduous", "🌳"),
    "Sorbus": ("Deciduous", "🌳"),
    "Tilia": ("Deciduous", "🌳"),
    "Ulmus": ("Deciduous", "🌳"),
    "Larix": ("Deciduous conifer", "🌲"),
    "Alces": ("Moose", "🫎"),
    "Anser": ("Goose", "🪿"),
    "Branta": ("Goose", "🪿"),
    # "Turdus": ("Blackbird", "🐦‍⬛"),
}
TAX_FAMILY = {
    "Cercopithecidae": ("Monkey", "🐒"),
    "Anatidae": ("Duck", "🦆"),
    "Formicidae": ("Ant", "🐜"),
    "Apidae": ("Bees", "🐝"),
    "Cactaceae": ("Cactus", "🌵"),
    "Arecaceae": ("Palms", "🌴"),
    "Aceraceae": ("Palms", "🌳"),
    "Culicidae": ("Mosquitoes", "🦟"),
    "Coccinellidae": ("Lady Beetle", "🐞"),
    "Delphinidae": ("Dolphin", "🐬"),
    "Platanistidae": ("Dolphin", "🐬"),
    "Iniidae": ("Dolphin", "🐬"),
    "Pontoporiidae": ("Dolphin", "🐬"),
    "Acanthuridae": ("Tropical Fish", "🐠"),
    "Pomacentridae": ("Tropical Fish", "🐠"),
    "Tetraodontidae": ("Blowfish", "🐡"),
    "Pinnipedia": ("Seals", "🦭"),
    "Crocodylidae": ("Crocodiles", "🐊"),
    "Serpentes": ("Snake", "🐍"),
    "Tyrannosauridae": ("T-Rex", "🦖"),
    "Spheniscidae": ("Penguins", "🐧"),
    "Accipitridae": ("Eagle", "🦅"),
    "Phoenicopteridae": ("Flamingos", "🦩"),
    "Leporidae": ("Rabbit", "🐇"),
    "Elephantidae": ("Elephant", "🐘"),
    "Phascolarctidae": ("Koala", "🐨"),
    "Cricetidae": ("Hamsters", "🐹"),
    "Ursidae": ("Bear", "🐻"),
    "Sciuridae": ("Chipmunks", "🐿"),
    "Cervidae": ("Deer", "🦌"),
    "Rhinocerotidae": ("Rhinoceros", "🦏"),
    "Giraffidae": ("Giraffe", "🦒"),
    "Erinaceidae": ("Hedgehog", "🦔"),
    "Hippopotamidae": ("Hippopotamus", "🦛"),
    "Megatherioidea": ("Sloth", "🦥"),
    "Choloepodidae": ("Sloth", "🦥"),
    "Bradypodidae": ("Sloth", "🦥"),
    "Mephitidae": ("Skunks", "🦨"),
    "Columbidae": ("Dove", "🕊️"),
    "Sauropodidae": ("Dinosaur", "🦕"),
    "Nephropidae": ("Lobster", "🦞"),
    "Ostreidae": ("Oyster", "🦪"),
    "Plethodontidae": ("Lizard", "🦎"),
    "Talitridae": ("Insects/Bug", "🐛"),
    # "Icteridae": ("Blackbird", "🐦‍⬛"),
}
TAX_ORDER = {
    "Fagales": ("Beeches, Oaks, Walnuts, And Allies", "🌳"),
    "Ericales": ("herbs", "🌿"),
    "Coleoptera": ("Beetle", "🪲"),
    "Araneae": ("Spider", "🕷"),
    "Scorpiones": ("Scorpion", "🦂"),
    "Lepidoptera": ("Butterfly", "🦋"),
    "Orthoptera": ("Cricket", "🦗"),
    "Diptera": ("Flies", "🪰"),
    "Blattodea": ("Cockroach", "🪳"),
    "Cetacea": ("Whale", "🐋"),
    "Octopoda": ("Octopus", "🐙"),
    "Tetraodontiformes": ("Tropical Fish", "🐠"),
    "Carcharhiniformes": ("Shark", "🦈"),
    "Heterodontiformes": ("Shark", "🦈"),
    "Orectolobiformes": ("Shark", "🦈"),
    "Lamniformes": ("Shark", "🦈"),
    "Hexanchiformes": ("Shark", "🦈"),
    "Pristiophoriformes": ("Shark", "🦈"),
    "Squaliformes": ("Shark", "🦈"),
    "Squatiniformes": ("Shark", "🦈"),
    "Anura": ("Frog", "🐸"),
    "Strigiformes": ("Owls", "🦉"),
    "Psittaciformes": ("Parrot", "🦜"),
    "Chiroptera": ("Bats", "🦇"),
    "Decapoda": ("Crab", "🦀"),
    "Myopsida": ("Squid", "🦑"),
    "Oegopsida": ("Squid", "🦑"),
    "Bathyteuthida": ("Squid", "🦑"),
    "Odonata": ("Mosquitoes", "🦟"),
    "Isopoda": ("Insects/Bug", "🐛"),
    "Perciformes": ("Fish", "🐟"),
    "Salmoniformes": ("Fish", "🐟"),
    "Cypriniformes": ("Fish", "🐟"),
    "Scorpaeniformes": ("Fish", "🐟"),
    "Caudata": ("Lizard", "🦎"),
}
TAX_CLASS = {
    "Gastropoda": ("Snail", "🐌"),
    "Bivalvia": ("Mollusca", "🐚"),
    "Actinopterygii": ("Fish", "🐟"),
    "Elasmobranchii": ("Fish", "🐟"),
    "Asteroidea": ("Fish", "🐟"),
    "Aves": ("Birds", "🐦"),
    "Pinopsida": ("Pines", "🌲"),
    "Coniferopsida": ("Conifers", "🌲"),
    "Testudines": ("Turtles", "🐢"),
    "Squamata": ("Lizard", "🦎"),
    "Insecta": ("Insects/Bug", "🐛"),
    "Mammalia": ("Mammal", "🐾"),
    "Arachnida": ("Spider", "🕷"),
    "Diplopoda": ("Worm", "🪱"),
    "Cubozoa": ("Jellyfish", "🪼"),
    "Scyphozoa": ("Jellyfish", "🪼"),
    "Staurozoa": ("Jellyfish", "🪼"),
    "Hydrozoa": ("Jellyfish", "🪼"),
    "Phaeophyceae": ("Corals", "🪸"),
    "Crocodylia": ("Crocodiles", "🐊"),
}
TAX_PHYLUM = {
    "Tracheophyta": ("plants", "🌱"),
    "Annelida": ("worms", "🪱"),
    "Nemertea": ("worms", "🪱"),
    "Arthropoda": ("Insects/Bug", "🐛"),
    "Cnidaria": ("Corals", "🪸"),
    "Ochrophyta": ("Corals", "🪸"),
    "Echinodermata": ("Fish", "🐟"),
}
TAX_KINGDOM = {
    "Fungi": ("Mushrom", "🍄"),
    "Protozoa": ("Mushrom", "🍄"),
    "Archaea": ("Microbe", "🦠"),
    "Plantae": ("plants", "🌱"),
    "Bacteria": ("Microbe", "🦠"),
    "Viruses": ("Microbe", "🦠"),
    "Chromista": ("Corals", "🪸"),
}

TAX_EMOJI = {
    "species": TAX_SPECIES,
    "genus": TAX_GENUS,
    "family": TAX_FAMILY,
    "order": TAX_ORDER,
    "class": TAX_CLASS,
    "phylum": TAX_PHYLUM,
    "kingdom": TAX_KINGDOM,
}


class importer:
    """Provides mapping function from Reddit endpoints to
    protobuf lbsnstructure
    """

    ORIGIN_NAME = "iNaturalist"
    ORIGIN_ID = 23

    def __init__(
        self,
        **_,
    ):
        # Create the OriginID globally
        # this OriginID is required for all CompositeKeys
        origin = lbsn.Origin()
        origin.origin_id = lbsn.Origin.INATURALIST
        self.origin = origin
        # this is where all the data will be stored
        self.lbsn_records = []
        self.lbsn_relationships = []
        self.null_island = 0
        self.log = logging.getLogger("__main__")
        self.skipped_low_geoaccuracy = 0
        # leaned on https://www.flickr.com/services/api/flickr.photos.licenses.getInfo.html
        # some of these are stubs, they do not exist (afaik) in the gbif data
        self.lic_dict = {
            "All Rights Reserved": 0,
            "Attribution-NonCommercial-ShareAlike License": 1,
            "CC_BY_NC_4_0": 2,
            "Attribution-NonCommercial-NoDerivs License": 3,
            "CC_BY_4_0": 4,
            "Attribution-ShareAlike License": 5,
            "Attribution-NoDerivs License": 6,
            "No known copyright restrictions": 7,
            "United States Government Work": 8,
            "CC0_1_0": 9,
            "Public Domain Mark": 10,
        }

    def parse_csv_record(self, record, *_):
        """Entry point for iNaturalist CSV data of type gbif

        Attributes:
        record          A single row from CSV, stored as dict type.
        """
        lbsn_records = self.extract_gbif_occurrence(record)
        return lbsn_records

    def extract_gbif_occurrence(self, record):
        """Main function for processing iNaturalist gbif CSV data.

        Overview of available columns and examples:
        0 gbifID    -   2460163310
        1 datasetKey    -   50c9509d-22c7-4a22-a47d-8c48425ef4a7
        2 occurrenceID     -   https://www.inaturalist.org/observations/33763208
        3 kingdom     -   Plantae
        4 phylum     -   Tracheophyta
        5 class   -   Magnoliopsida
        6 order     -   Lamiales
        7 family    -   family
        8 genus     -   Prunella
        9 species      -     Prunella vulgaris
        10 scientificName   -   Prunella vulgaris L.
        11 verbatimScientificName   - Prunella vulgaris
        12 verbatimScientificNameAuthorship    -   Gyps fulvus
        13 countryCode     -   US
        14 locality -   IT
        15 stateProvince -   Massachusetts
        16 occurrenceStatus -   PRESENT
        17 individualCount -   PRESENT
        18 publishingOrgKey  -   28eb1a3f-1c15-4a95-931a-4af90ecb574d
        19 decimalLatitude    -   42.451464
        20 decimalLongitude  -   -71.123464
        21 coordinateUncertaintyInMeters   -   10.0
        22 coordinatePrecision  -   829.0
        23 elevation  -   31373.0
        24 elevationAccuracy    -   30.0
        25 depth
        26 depthAccuracy
        27 eventDate - 2019-10-02T11:35:00
        28 day - 2
        29 month - 10
        30 year - 2019
        31 taxonKey - 5341297
        32 speciesKey - 5341297
        33 basisOfRecord - HUMAN_OBSERVATION
        34 institutionCode - iNaturalist
        35 collectionCode - Observations
        36 catalogNumber - 33763208
        37 recordNumber - 34119680
        38 identifiedBy - Claire Nesterova
        39 dateIdentified - 2019-10-02T18:34:24
        40 license - CC_BY_NC_4_0
        41 rightsHolder - Claire Nesterova
        42 recordedBy - Claire Nesterova
        43 typeStatus - Gianmaria Marchese
        44 establishmentMeans
        45 lastInterpreted - 2023-05-10T00:45:38.276Z
        46 mediaType - StillImage;StillImage
        47 issue

        """
        # note that one input record may contain many lbsn records
        # therefore, return list of processed records
        lbsn_records = []
        # start mapping input to lbsn_records
        post_guid = record.get("occurrenceID")

        if not HF.check_notice_empty_post_guid(post_guid):
            return None
        post_guid = self.strip_occurence_guid(post_guid)
        post_record = HF.new_lbsn_record_with_id(lbsn.Post(), post_guid, self.origin)

        # the user ID is not provided in gbif;
        # in order to normalize for recurring users, a user ref is
        # recommended in lbsn
        # therefore, we generate a hash based on the name given in gbif;
        # this leads to collisions in case of repeating names, but
        # was preferred over having no normalization at all
        user_ref = record.get("identifiedBy")
        if not user_ref:
            user_ref = record.get("rightsHolder")
        if not user_ref:
            user_ref = record.get("recordedBy")
        user_name = user_ref
        user_guid = hashlib.md5(user_ref.encode("utf-8")).hexdigest()
        user_record = HF.new_lbsn_record_with_id(lbsn.User(), user_guid, self.origin)
        user_record.user_name = user_name
        if user_record:
            post_record.user_pkey.CopyFrom(user_record.pkey)
        lbsn_records.append(user_record)

        post_record.post_latlng = self.gbif_extract_postlatlng(
            lat_entry=record.get("decimalLatitude"),
            lng_entry=record.get("decimalLongitude"),
        )
        geoaccuracy = importer.gbif_map_geoaccuracy(
            record.get("coordinateUncertaintyInMeters")
        )
        if geoaccuracy:
            post_record.post_geoaccuracy = geoaccuracy
        country_ref = record.get("countryCode")
        if country_ref:
            country_record = HF.new_lbsn_record_with_id(
                lbsn.Country(), country_ref, self.origin
            )
            lbsn_records.append(country_record)
            post_record.country_pkey.CopyFrom(country_record.pkey)
        # gbif comes without timezone, see [1] and [2], so we treat it that way
        # [1]: https://github.com/gbif/gbif-api/issues/3
        # [2]: https://github.com/gbif/portal-feedback/issues/548
        publish_ref = record.get("dateIdentified")
        if publish_ref:
            date_time_record = datetime.strptime(publish_ref, TIME_FORMAT)
            publish_proto = HF.date_to_proto(date_time_record)
            if publish_proto:
                post_record.post_publish_date.CopyFrom(publish_proto)
        created_ref = record.get("eventDate")
        if created_ref:
            date_time_record = datetime.strptime(created_ref, TIME_FORMAT)
            created_proto = HF.date_to_proto(date_time_record)
            if created_proto:
                post_record.post_create_date.CopyFrom(created_proto)
        # post_record.post_views_count = 0
        # post_record.post_comment_count = 0
        # post_record.post_like_count = 0
        post_record.post_url = record.get("occurrenceID")
        # this assignment is opinionated:
        # the species name is partly automatically derived on iNaturalist;
        # or assigned based on the common name given by the user;
        # the post_filter attribute in the lbsnstructure can also refer to
        # such automatic assignments [1]
        # https://lbsn.vgiscience.org/protobuf/#lbsn.structure.Post;
        # Title and description, or comments, are reserved for user added texts,
        # available from the original data on iNaturalist
        post_record.post_filter = record.get("species")
        # another convention:
        # the kingdom (Plantae, Fungi, Animalia) is assigned to "topic_group"
        post_record.topic_group.append(record.get("kingdom"))
        # post_record.post_body = ""
        # post_record.post_title = ""
        # post_record.post_thumbnail_url = ""
        post_record.post_type = lbsn.Post.IMAGE
        # replace text-string of content license by integer-id
        license_ref = record.get("license")
        if license_ref:
            license_id = self.get_license_number_from_license_name(license_ref)
            if license_id:
                post_record.post_content_license = license_id
        # species to emoji
        emoji = importer.map_species_emoji(record, tax_emoji=TAX_EMOJI)
        if emoji:
            post_record.emoji.extend([emoji])
        lbsn_records.append(post_record)
        return lbsn_records

    @staticmethod
    def strip_occurence_guid(occurrence_id: str) -> str:
        """Strip inaturalist prefix from occurrence guid"""
        return occurrence_id.rsplit("/", 1)[-1]

    def gbif_extract_postlatlng(self, lat_entry: str, lng_entry: str) -> str:
        """Basic routine for extracting lat/lng coordinates from post.
        - checks for consistency and errors
        - in case of any issue, entry is submitted to Null island (0, 0)
        """
        if lat_entry == "" and lng_entry == "":
            l_lat, l_lng = 0, 0
        else:
            try:
                l_lng = Decimal(lng_entry)
                l_lat = Decimal(lat_entry)
            except ValueError:
                l_lat, l_lng = 0, 0
        if (
            (l_lat == 0 and l_lng == 0)
            or l_lat > 90
            or l_lat < -90
            or l_lng > 180
            or l_lng < -180
        ):
            l_lat, l_lng = 0, 0
            self.send_to_null_island()
        return importer.lat_lng_to_wkt(l_lat, l_lng)

    @staticmethod
    def lat_lng_to_wkt(lat, lng):
        """Convert lat lng to WKT (Well-Known-Text)"""
        point_latlng_string = "POINT(%s %s)" % (lng, lat)
        return point_latlng_string

    def send_to_null_island(self):
        """Logs entries with problematic lat/lng's,
        increases Null Island Counter by 1.
        """
        self.null_island += 1

    @staticmethod
    def gbif_map_geoaccuracy(gbif_geo_accuracy_meters):
        """Gbif Geoaccuracy Levels (coordinateUncertaintyInMeters) is mapped to four
           LBSNstructure levels (LBSN PostGeoaccuracy):
           UNKNOWN = 0; LATLNG = 1; PLACE = 2; CITY = 3; COUNTRY = 4

        Attributes:
        gbif_geo_accuracy_meters   Geoaccuracy in meters returned from gbif
        """
        if not gbif_geo_accuracy_meters:
            # per default, if no coordinateUncertaintyInMeters exists
            # assume highest geo accuracy
            return lbsn.Post.LATLNG
        try:
            meters_accuracy = abs(float(gbif_geo_accuracy_meters))
        except ValueError:
            return
        if meters_accuracy <= 100:
            return lbsn.Post.LATLNG
        elif meters_accuracy <= 1000:
            return lbsn.Post.PLACE
        elif meters_accuracy <= 30000:
            return lbsn.Post.CITY
        else:
            return lbsn.Post.COUNTRY

    def get_license_number_from_license_name(self, license_name: str) -> Optional[int]:
        """gbif contains only full string names of licenses
        This function converts names to ids.

        Arguments:
            license_name {str} -- gbif license name
        ids leaned on:
        https://www.flickr.com/services/api/flickr.photos.licenses.getInfo.html
        """
        lic_number = self.lic_dict.get(license_name)
        return lic_number

    @staticmethod
    def map_species_emoji(
        record: Dict[str, str],
        tax_emoji: Dict[str, Dict[str, Tuple[str, str]]],
    ) -> Optional[str]:
        """
        There is currently no user-created "body" of information included in the gbif data,
        the gbif data does not contain direct user input, just the matched scientific
        identifiers. An idea to include user input reference could be to
        translate scientific identifiers to "Nature Emoji", e.g. as listed
        here [1]. This method here is a WIP of this idea.

        The tax groups are assigned based on gbif classification, e.g. [2] for Rat.
        The emoji assignment starts with the most detailed species classification, and then
        considers broader taxonomic hierarchies (e.g. Kingdom "Fungi" is assigned to
        general Mushrom emoji, after more specific emoji have been assigned, if available).

        - convert codepoints with:
            s='U+1F412'
            chr(int(s[2:], 16))

        - check in LBSN DB:
        ```
        SELECT * FROM topical.post WHERE array_length(emoji, 1) > 0;
        ```
        - for updating empty mappings:
        ```
        SELECT emoji,post_url,array_length(emoji, 1) AS ct FROM topical.post ORDER BY ct DESC
        ```

        [1]: https://symbl.cc/en/emoji/animals-and-nature/
        [2]: https://www.gbif.org/species/5510
        """

        emoji_mapping = importer.get_dict_entry(record, tax_emoji)
        if emoji_mapping:
            return emoji_mapping

    @staticmethod
    def get_dict_entry(record, tax_emoj):
        """Return first emoji-match if record found in tax_emoj"""
        level_list = [
            "species",
            "genus",
            "family",
            "order",
            "class",
            "phylum",
            "kingdom",
        ]
        for tax_level in level_list:
            tax_level_dict = tax_emoj.get(tax_level)
            match_test = tax_level_dict.get(record.get(tax_level))
            if match_test:
                return match_test[1]
