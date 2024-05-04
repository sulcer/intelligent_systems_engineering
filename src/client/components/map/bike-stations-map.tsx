'use client';
import React from 'react';
import {APIProvider, Map} from '@vis.gl/react-google-maps';
import {useRouter} from "next/navigation";
import {useBikeStations} from "@/lib/hooks/bike-stations";
import PredictionDialog from "@/components/prediction/prediction-dialog";
import Header from "@/components/ui/Header";

const BikeStationsMap = () => {
    const router = useRouter();
    const {data: stations = []} = useBikeStations();

    return (
        <>
            <Header />
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
                        <PredictionDialog
                            key={station.number}
                            stationNumber={station.number}
                            lat={station.position.lat}
                            lon={station.position.lng}
                        />
                    ))}
                </Map>
            </APIProvider>
        </>
    );
};

export default BikeStationsMap;