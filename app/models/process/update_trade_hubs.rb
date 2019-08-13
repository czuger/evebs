module Process

  # This class should disappear as the TradeHub class should no longer be a used class.
  class UpdateTradeHubs

    TRADE_HUBS_IDS = [10000020, 30001021, 30001041, 30004738, 30002440, 30000903, 30004504, 30000718, 30001833, 30001842, 30001858, 30003278, 30003286, 30003361, 30001277, 145365801, 30004299, 30045329, 30000109, 30002964, 30002187, 30004969, 30005001, 30003010, 30005216, 30002510, 30002544, 30002545, 30004078, 30003862, 30005055, 30005060, 30001363, 30001376, 30001429, 30002053, 30002385, 30003794, 30003830, 30002659, 30003574, 30003064, 30002819, 30000142, 30045305, 30005323]

    def self.update
      TradeHub.transaction do
        TRADE_HUBS_IDS.each do |id|
          system = UniverseSystem.find_by_cpp_system_id( id )

          raise unless system

          TradeHub.find_or_create_by!( eve_system_id: id ) do |record|
            record.name = system.name

          end
        end
      end
    end

  end

end

