module Process

  class UpdateEveItems

    def update
      Banner.p 'About to update items'

      types = YAML::load_file('data/types.yaml')
      cpp_market_prices = YAML::load_file('data/cpp_market_prices.yaml')

      lowest_production_level = 0

      blueprint_cpp_to_syntetic_key_conversion_hash = Hash[ Blueprint.pluck( :produced_cpp_type_id, :id ) ]
      market_groups_cpp_to_syntetic_key_conversion_hash = Hash[ MarketGroup.pluck( :cpp_market_group_id, :id ) ]

      types_to_destroy = EveItem.pluck( :cpp_eve_item_id ) - types.keys
      EveItem.where( cpp_eve_item_id: types_to_destroy ).destroy_all

      types.values.each do |type|
        on_db_item = EveItem.where( cpp_eve_item_id: type[:cpp_eve_item_id] ).first_or_initialize

        on_db_item.volume = type[:volume]
        on_db_item.name = type[:name]
        on_db_item.blueprint_id = blueprint_cpp_to_syntetic_key_conversion_hash[type[:cpp_eve_item_id]]

        on_db_item.production_level = type[:production_level]
        lowest_production_level = [ lowest_production_level, type[:production_level] ].min
        on_db_item.base_item = type[:base_item]

        on_db_item.market_group_id = market_groups_cpp_to_syntetic_key_conversion_hash[ type[:market_group_id] ]

        mp_data = cpp_market_prices[type[:cpp_eve_item_id].to_i]
        if mp_data
          on_db_item.cpp_market_adjusted_price = mp_data['adjusted_price']
          on_db_item.cpp_market_average_price = mp_data['average_price']
        end

        on_db_item.save
      end

      File.open('data/lowest_production_level', 'w') {|f| f.write lowest_production_level }
    end
  end

end

