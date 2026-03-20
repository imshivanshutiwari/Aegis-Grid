import React, { useMemo, useState, useEffect } from 'react';
import DeckGL from '@deck.gl/react';
import { ScatterplotLayer, PathLayer, PolygonLayer, TextLayer } from '@deck.gl/layers';
import { HeatmapLayer } from '@deck.gl/aggregation-layers';
import { Map } from 'react-map-gl';
import maplibregl from 'maplibre-gl';
import { useStore } from '../store';

const MAP_STYLE = 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json';

const INITIAL_VIEW_STATE = { longitude: 0, latitude: 0, zoom: 10, pitch: 45, bearing: 0 };

export default function TacticalMap() {
  const units = useStore(state => state.units);
  const alerts = useStore(state => state.alerts);
  const gpsJammed = useStore(state => state.gpsJammed);

  // Interpolation state
  const [interpolatedUnits, setInterpolatedUnits] = useState([]);

  useEffect(() => {
    // A mock linear interpolation worker would be implemented here.
    // Setting directly to simulate real-time updates for now.
    setInterpolatedUnits(units);
  }, [units]);

  const getUnitColor = (type) => {
    switch (type) {
      case 'FRIENDLY': return [0, 100, 255];
      case 'HOSTILE': return [255, 0, 0];
      case 'UNKNOWN': return [255, 255, 0];
      default: return [128, 128, 128];
    }
  };

  const layers = [
    new HeatmapLayer({
        id: 'threat-heatmap',
        data: alerts,
        getPosition: d => [d.lon || 0, d.lat || 0],
        getWeight: d => d.threat_score || 0.5,
        radiusPixels: 60,
        intensity: 1,
        threshold: 0.1
    }),
    new ScatterplotLayer({
      id: 'units-layer',
      data: interpolatedUnits,
      pickable: true,
      opacity: 0.8,
      stroked: true,
      filled: true,
      radiusScale: 10,
      radiusMinPixels: 5,
      radiusMaxPixels: 100,
      lineWidthMinPixels: 1,
      getPosition: d => [d.lon, d.lat],
      getFillColor: d => getUnitColor(d.unit_type),
      getLineColor: d => [255, 255, 255],
    }),
    new ScatterplotLayer({
        id: 'uncertainty-layer',
        data: gpsJammed ? interpolatedUnits : [],
        pickable: false,
        opacity: 0.3,
        stroked: true,
        filled: true,
        radiusScale: 50,
        getPosition: d => [d.lon, d.lat],
        getFillColor: [255, 165, 0, 100],
        getLineColor: [255, 165, 0, 200]
    }),
    new TextLayer({
        id: 'text-layer',
        data: interpolatedUnits,
        getPosition: d => [d.lon, d.lat],
        getText: d => d.id.substring(0, 4),
        getSize: 12,
        getColor: [255, 255, 255],
        getPixelOffset: [0, -20],
    })
  ];

  return (
    <DeckGL initialViewState={INITIAL_VIEW_STATE} controller={true} layers={layers}
            getTooltip={({object}) => object && `${object.unit_type}\nID: ${object.id}\nThreat: ${object.threat_level || 'N/A'}`}>
      <Map mapStyle={MAP_STYLE} mapLib={maplibregl} />
    </DeckGL>
  );
}
