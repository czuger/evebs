module Process
  class UpdateTradeVolumeEstimationFromDownloadedHistoryData < UpdateBase

    def update
      Misc::Banner.p 'About to update region_volume_downloaded in TradeVolumeEstimation'

      TradeVolumeEstimation.transaction do
        transaction_update
      end

      Misc::Banner.p 'Update region_volume_downloaded in TradeVolumeEstimation finished'
    end

    def transaction_update
      1.upto(Esi::DownloadHistoryReadItemsLists::PROCESSES_COUNT).each do |process_id|

        File.open( "data/regional_sales_volumes_#{process_id}.json_stream", 'r' ) do |f|
          f.each do |line|
            data = JSON.parse( line )

            TradeVolumeEstimation.where( cpp_type_id: data['cpp_type_id'], cpp_region_id: data['cpp_region_id'] ).
                update_all( region_volume_downloaded_from_history: data['volume'] )
          end
        end
      end
    end
  end
end
