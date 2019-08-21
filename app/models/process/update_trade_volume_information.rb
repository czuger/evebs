module Process
  class UpdateTradeVolumeInformation < UpdateBase

    def update

      Misc::Banner.p 'About to update region_volume_downloaded in TradeVolumeEstimation'

      eve_item_conversion_hash ||= Hash[ EveItem.pluck( :cpp_eve_item_id, :id ) ]

      TradeVolumeEstimation.transaction do
        1.upto(Esi::DownloadHistoryReadItemsLists::PROCESSES_COUNT).each do |process_id|

          File.open( "data/regional_sales_volumes_#{process_id}.json_stream", 'r' ) do |f|
            f.each do |line|
              data = JSON.parse( line )

              eve_item_id = eve_item_conversion_hash[data['cpp_type_id']]
              next unless eve_item_id

              systems = UniverseSystem.joins( { universe_constellation: :universe_region } ).
                  where( 'universe_regions.cpp_region_id = ?', data['cpp_region_id'] )

              TradeVolumeEstimation.
                  where( eve_item_id: eve_item_id ).
                  where( universe_system: systems ).
                  update_all( region_volume_downloaded: data['volume'] )
            end
          end
        end
      end

      Sql::UpdateVolumeFromVolumeEstimations.execute
    end

  end
end
