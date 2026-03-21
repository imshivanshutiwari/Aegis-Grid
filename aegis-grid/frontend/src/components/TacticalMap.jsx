import React, { useState, useEffect } from 'react';
import DeckGL from '@deck.gl/react';
import { ScatterplotLayer, TextLayer } from '@deck.gl/layers';
import { HeatmapLayer } from '@deck.gl/aggregation-layers';
import { Map } from 'react-map-gl';
import maplibregl from 'maplibre-gl';
import { useStore } from '../store';

const MAP_STYLE = 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json';
const INITIAL_VIEW_STATE = { longitude: 120.5, latitude: 24.5, zoom: 7, pitch: 45, bearing: 0 };


export default function TacticalMap() {
  const units = useStore(state => state.units);
  const alerts = useStore(state => state.alerts);
  const gpsJammed = useStore(state => state.gpsJammed);

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
      data: units,
      pickable: true,
      opacity: 0.8,
      stroked: true,
      filled: true,
      radiusScale: 10,
      radiusMinPixels: 5,
      radiusMaxPixels: 100,
      lineWidthMinPixels: 1,
      getPosition: d => {
        const noise = gpsJammed ? (Math.random() - 0.5) * 0.02 : 0;
        return [d.lon + noise, d.lat + noise];
      },
      getFillColor: d => getUnitColor(d.unit_type),
      getLineColor: d => [255, 255, 255],
    }),
    new ScatterplotLayer({
        id: 'uncertainty-layer',
        data: gpsJammed ? units : [],
        pickable: false,
        opacity: 0.2,
        stroked: true,
        filled: true,
        radiusScale: 100,
        radiusMinPixels: 20,
        getPosition: d => [d.lon, d.lat],
        getFillColor: [255, 100, 0, 40],
        getLineColor: [255, 100, 0, 80],
        updateTriggers: {
          data: [gpsJammed]
        }
    }),
    new TextLayer({
        id: 'text-layer',
        data: units,
        getPosition: d => {
          const noise = gpsJammed ? (Math.random() - 0.5) * 0.1 : 0;
          return [d.lon + noise, d.lat + noise];
        },
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
