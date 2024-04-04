'use client';
import React from 'react';
import {APIProvider, Map} from '@vis.gl/react-google-maps';
import StationMarker from "@/components/map/station-marker";
import {useRouter} from "next/navigation";
import {useBikeStations} from "@/lib/hooks/bike-stations";

const BikeStationsMap = () => {
    const router = useRouter();
    const {data: stations = []} = useBikeStations();

    console.log(stations);

    return (
        <div>
            <APIProvider apiKey={process.env.NEXT_PUBLIC_GOOGLE_MAPS_KEY as string}>
                <Map
                    style={{width: '100vw', height: '100vh'}}
                    defaultCenter={{lat: 46.5547, lng: 15.6467}}
                    defaultZoom={16}
                    gestureHandling={'greedy'}
                    disableDefaultUI={true}
                    mapId={'map-id'}
                >
                    {stations.map(station => (
                        <StationMarker
                            key={station.number}
                            lat={station.position.lat}
                            lon={station.position.lng}
                            number={station.number}
                            onClick={() => router.push(`/bike-station/${station.number}`)}
                        />
                    ))}
                </Map>
            </APIProvider>
        </div>
    );
};

export default BikeStationsMap;