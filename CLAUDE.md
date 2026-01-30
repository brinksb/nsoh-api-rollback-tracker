# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

NSOH API Rollback Tracker detects data rollbacks in the National Storm Overflow Hub (NSOH). Thames Water publishes storm overflow event data to NSOH, but the published data sometimes reverts to previous readings. This tool compares the source API with NSOH to identify when rollbacks occur.

## Key APIs

- **Thames Water API**: `https://api.thameswater.co.uk/opendata/v2/discharge/status` - Source of truth for discharge status
- **NSOH Dataset**: `https://www.streamwaterdata.co.uk/datasets/216f455c4435450693cf1d0d0ecf6023_0/explore` - Published geospatial layer to monitor

## Architecture Goals

- Ingest from both APIs every 3 minutes (configurable)
- Compare readings to detect NSOH rollbacks
- Infrastructure should be free-tier and programmatically provisionable
