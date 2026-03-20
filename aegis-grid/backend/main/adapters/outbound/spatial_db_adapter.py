import asyncpg
import logging
from typing import List, Optional, Tuple, Dict, Any
from main.infrastructure.config.settings import settings

logger = logging.getLogger(__name__)

class SpatialDBAdapter:
    """Async PostGIS connection adapter with CQRS separation via raw SQL."""
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        try:
            self.pool = await asyncpg.create_pool(self.database_url)
            logger.info("Connected to PostGIS database.")
            await self._initialize_schema()
        except Exception as e:
            logger.error(f"Failed to connect to PostGIS: {e}")
            raise e

    async def _initialize_schema(self):
        """Create tables and explicitly create GIST indices."""
        schema_sql = """
        CREATE TABLE IF NOT EXISTS units (
            id UUID PRIMARY KEY,
            unit_type VARCHAR(50),
            threat_level VARCHAR(50),
            location GEOMETRY(Point, 4326),
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_units_location ON units USING GIST (location);
        """
        async with self.pool.acquire() as conn:
            await conn.execute(schema_sql)

    async def close(self):
        if self.pool:
            await self.pool.close()
            logger.info("Closed PostGIS connection.")

    async def get_unit_location(self, unit_id: str) -> Optional[Tuple[float, float]]:
        query = """
        SELECT ST_X(location) as lon, ST_Y(location) as lat
        FROM units
        WHERE id = $1
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, unit_id)
            if row:
                return (row['lon'], row['lat'])
            return None

    async def get_units_within(self, lon: float, lat: float, radius_meters: float) -> List[Dict[str, Any]]:
        """Uses ST_DWithin and GIST index."""
        query = """
        SELECT id, unit_type, threat_level, ST_X(location) as lon, ST_Y(location) as lat
        FROM units
        WHERE ST_DWithin(location::geography, ST_SetSRID(ST_MakePoint($1, $2), 4326)::geography, $3)
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, lon, lat, radius_meters)
            return [dict(row) for row in rows]

    async def update_unit_location(self, unit_id: str, unit_type: str, lon: float, lat: float):
        """CQRS Write Command."""
        query = """
        INSERT INTO units (id, unit_type, location)
        VALUES ($1, $2, ST_SetSRID(ST_MakePoint($3, $4), 4326))
        ON CONFLICT (id) DO UPDATE
        SET location = EXCLUDED.location,
            last_updated = CURRENT_TIMESTAMP
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query, unit_id, unit_type, lon, lat)

spatial_db = SpatialDBAdapter(settings.database_url)
