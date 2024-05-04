import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import React, {FC} from "react";
import {useBikeStationByNumber, useBikeStationPredictions} from "@/lib/hooks/bike-stations";
import LoadingSpinner from "@/components/ui/loading-spinner";
import Table from "@/components/ui/table";
import StationMarker from "@/components/map/station-marker";

interface PredictionDialogProps {
  stationNumber: number;
  lat: number;
  lon: number;
}
const PredictionDialog: FC<PredictionDialogProps> = ({ stationNumber, lat, lon }) => {
  const { data: station, isLoading, isError } = useBikeStationByNumber(Number(stationNumber));
  const { data: predictions, isLoading: isLoadingPredictions, isError: isErrorPredictions } = useBikeStationPredictions(Number(stationNumber), 7);

  return (
      <Dialog>
        <DialogTrigger asChild>
            <StationMarker
                            lat={lat}
                            lon={lon}
                            number={stationNumber}
                            onClick={() => {console.log("station: ", stationNumber)}}
                        />
        </DialogTrigger>
        <DialogContent className="sm:max-w-[570px]">
          {isLoading ? <LoadingSpinner/> :
              <>
                <DialogHeader>
                  <DialogTitle>{station?.name}</DialogTitle>
                  <DialogDescription>
                    {station?.address}
                  </DialogDescription>
                  <DialogDescription>
                    Station number: {stationNumber}
                  </DialogDescription>
                </DialogHeader>
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
              </>
          }
        </DialogContent>
      </Dialog>
  )
}

export default PredictionDialog;