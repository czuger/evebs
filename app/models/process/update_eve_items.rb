module Process

  class UpdateEveItems

    def update
      Misc::Banner.p 'About to update items'

      EveItem.transaction do
        transact_update
      end

      Misc::Banner.p 'Update items finished'
    end

    private

    def transact_update
      crlf = /(\r\n|\n\r|\r|\n)/

      types = YAML::load_file('data/types.yaml')

      blueprint_cpp_to_syntetic_key_conversion_hash = Hash[ Blueprint.pluck( :produced_cpp_type_id, :id ) ]
      market_groups_cpp_to_syntetic_key_conversion_hash = Hash[ MarketGroup.pluck( :cpp_market_group_id, :id ) ]

      # types_to_destroy = EveItem.pluck( :cpp_eve_item_id ) - types.keys
      # EveItem.where( cpp_eve_item_id: types_to_destroy ).destroy_all

      types.values.each do |type|

        on_db_item = EveItem.where( cpp_eve_item_id: type[:cpp_eve_item_id] ).first_or_initialize

        on_db_item.volume = type[:volume]
        on_db_item.name = type[:name]
        on_db_item.description = type[:desc].gsub( crlf, '<br>' )
        on_db_item.description.gsub!( /showinfo:/, 'https://eveinfo.com/item/' )

        on_db_item.packaged_volume = type[:packaged_volume].to_f
        on_db_item.mass = type[:mass].to_f

        on_db_item.blueprint_id = blueprint_cpp_to_syntetic_key_conversion_hash[type[:cpp_eve_item_id]]

        on_db_item.base_item = false

        on_db_item.market_group_id = market_groups_cpp_to_syntetic_key_conversion_hash[ type[:market_group_id] ]

        on_db_item.faction = (type[:meta_level] ? type[:meta_level] : 0) >= 6

        on_db_item.save!

        if on_db_item.market_group_id
          on_db_item.market_group_path = [ on_db_item.market_group.ancestors.map{ |e| { name: e.name, id: e.id } }.reverse, { name: on_db_item.market_group.name, id: on_db_item.market_group_id } ].flatten
        end

        on_db_item.save!
      end
    end
  end

end

