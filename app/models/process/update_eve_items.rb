module Process

  class UpdateEveItems

    def update
      Banner.p 'About to update items'

      types = YAML::load_file('data/types.yaml')

      lowest_production_level = 0

      @blueprint_cpp_to_syntetic_key_conversion_hash = Hash[ Blueprint.pluck( :produced_cpp_type_id, :id ) ]

      types_to_destroy = EveItem.pluck( :cpp_eve_item_id ) - types.keys
      EveItem.where( cpp_eve_item_id: types_to_destroy ).destroy_all

      types.values.each do |type|
        on_db_item = EveItem.where( cpp_eve_item_id: type[:cpp_eve_item_id] ).first_or_initialize

        on_db_item.volume = type[:volume]
        on_db_item.name = type[:name]
        on_db_item.blueprint_id = @blueprint_cpp_to_syntetic_key_conversion_hash[type[:cpp_eve_item_id]]

        on_db_item.production_level = type[:production_level]
        lowest_production_level = [ lowest_production_level, type[:production_level] ].min
        on_db_item.base_item = type[:base_item]

        on_db_item.save
      end

      File.open('data/lowest_production_level', 'w') {|f| f.write lowest_production_level }
    end
  end

end

