'use client';
import Table from "@/components/ui/table";
import Link from "next/link";
import {useBikeStationByNumber, useBikeStationPredictions} from "@/lib/hooks/bike-stations";
import LoadingSpinner from "@/components/ui/loading-spinner";

interface PageProps {
    params: {
        stationNumber: string;
    }
}

const Page = ({params}: PageProps) => {
    const { data: station, isLoading, isError } = useBikeStationByNumber(Number(params.stationNumber));
    const { data: predictions, isLoading: isLoadingPredictions, isError: isErrorPredictions } = useBikeStationPredictions(Number(params.stationNumber), 7);

    return (
        <div className={'m-5'}>
            {isLoading ? <LoadingSpinner /> :
                <>
                    <h1 className={'text-xl font-bold'}>{station?.name}</h1>
                    <p className={'text-sm text-gray-500'}>{station?.address}</p>
                    <p className={'text-sm text-gray-500'}>Station number: {params.stationNumber}</p>


                    <div>
                        <p className={'font-semibold'}>Currently:</p>
                        <div className={'flex flex-row gap-5'}>
                            <div className={'flex flex-col items-center'}>
                                <p className={'text-4xl font-bold'}>{station?.available_bikes}</p>
                                <p className={'text-sm text-gray-500'}>bikes</p>
                            </div>
                            <div className={'flex flex-col items-center'}>
                                <p className={'text-4xl font-bold'}>{station?.available_bike_stands}</p>
                                <p className={'text-sm text-gray-500'}>free stands</p>
                            </div>
                        </div>
                    </div>

                    {isLoadingPredictions ? <p className={'text-sm text-gray-500'}>Predicting...</p> :
                        <Table rows={predictions as any[]}/>}

                    <div className={'mt-5'}>
                        <Link className={'bg-red-500 text-white p-2 rounded-md'} href={'/'}>Bike Map</Link>
                    </div>
                </>
            }
        </div>
    );
};

export default Page;