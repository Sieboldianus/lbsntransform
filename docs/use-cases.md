If you're using the command line interface, a common usage of lbsntransform is to
import/convert arbitrary social media data, e.g. from Flickr or Twitter, to a Postgres Database
with the [common lbsn structure](https://lbsn.vgiscience.org/)

The following two primary use cases exist:

1. **Importing lbsntransform as a package**
   Use this approach to convert data, such as individual posts 
   retrieved from an API, on-the-fly (in-memory), in your own
   python package.

2. **Using the command line interface (cli) to perform batch conversions**
   Use this approach if you want to convert batches of data stored as
   arbitrary json/csv files, or if you want to convert from a database 
   with the raw lbsn structure to a database with the privacy-aware hll 
   format.

For any conversion,  

- the input type must be provided, see [input-types](../input-types)  
- a mapping must exist, see [input-mappings](../mappings/#input-mappings)  
