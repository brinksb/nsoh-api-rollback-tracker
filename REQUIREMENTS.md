NSOH rollback bug

We (Thames Water) is hosting an API end-point called the EDM discharge end-point. It is a status endpoint of all the places in the Thames Water area where storm overflow events are happening. We have in internal API end-point, and we are publishing it as a geospatial layer to the National Storm Overflow hub. However, we are seeing that, after it’s ingested into NSOH, sometimes we see ‘rollbacks’, i.e., the data reverts to the previous reading. I need to show our team that it’s happening, so that the geospatial team can see it exists, and then attempt to fix it.

Our API: https://api.thameswater.co.uk/opendata/v2/discharge/status
NSOH: https://www.streamwaterdata.co.uk/datasets/216f455c4435450693cf1d0d0ecf6023_0/explore?location=51.622454%2C-0.829212%2C8&showTable=true

I need recommendations on how to ingest both (default 3 minutes), then do a comparison, and then detect if the NSOH does a rollback.

First we need to see if we can do the ingestions, then think of an architecture for both ingesting it and showing it (ideally free, on some of the main services, that you can provision programatically) Then we can iterate on persistence and visualisation.
