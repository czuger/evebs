module Process
  class UpdateTradeVolumeEstimationsFromPublicTradeOrders < UpdateBase

    def update
      Misc::Banner.p 'About to update TradeVolumeEstimation from public trades orders'

      TradeVolumeEstimation.transaction do
        transaction_update
      end

      Misc::Banner.p 'Update of TradeVolumeEstimation from public trades orders finished'
    end

    private

    def transaction_update
      # TradeVolumeEstimation.connection.truncate('trade_volume_estimations')

      estimations = {}

      puts 'About to sum volumes per type and system' if @verbose_output

      File.open( 'data/public_trades_orders.json_stream', 'r' ) do |f|
        f.each do |line|
          data = JSON.parse( line )

          next if data['is_buy_order']

          cpp_system_id = data['system_id']
          cpp_type_id = data['type_id']

          estimations[cpp_type_id] ||= {}

          estimations[cpp_type_id][cpp_system_id] ||= 0
          estimations[cpp_type_id][cpp_system_id] += data['volume_total']
        end
      end

      puts 'Per type and system volume sum finished' if @verbose_output

      estimations_import_buffer = []

      estimations.each_pair do |cpp_type_id, val|
        val.each_pair do |cpp_system_id, volume|
          estimations_import_buffer << TradeVolumeEstimation.new( cpp_system_id: cpp_system_id, cpp_type_id: cpp_type_id, trade_hub_volume_computed_from_orders: volume )
        end
      end

      TradeVolumeEstimation.import( estimations_import_buffer,
                                    on_duplicate_key_update: {conflict_target: [:cpp_system_id, :cpp_type_id],
                                                              columns: [:trade_hub_volume_computed_from_orders] } )

      Sql::UpdateTradeVolumeEstimationsPublicOrdersData.execute
    end

  end
end
