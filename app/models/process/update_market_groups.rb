module Process

  class UpdateMarketGroups

    # Il faut récupérer les parents et les parents de ces groupes.
    def update
      Misc::Banner.p 'About to update market groups'

      market_groups = YAML::load_file('data/market_groups.yaml')

      market_groups.values.each do |mg|
        group = MarketGroup.where( cpp_market_group_id: mg[:market_group_id] ).first_or_initialize
        group.name = mg[:name]
        group.cpp_parent_market_group_id = mg[:parent_group_id]
        group.save!
      end

      MarketGroup.all.each do |mg|
        mg.parent_id = MarketGroup.find_by_cpp_market_group_id( mg.cpp_parent_market_group_id )&.id
        mg.save!
      end

      used_market_group_ids = Set.new

      market_groups.keys.each do |key|
        used_market_group_ids << key
        used_market_group_ids += MarketGroup.find_by_cpp_market_group_id( key ).ancestors.map{ |a| a.cpp_market_group_id }
      end

      # Need to fix this
      # market_groups_to_destroy_ids = MarketGroup.pluck( :cpp_market_group_id ) - used_market_group_ids.to_a
      #
      # blueprints_linked_to_items_ids = BlueprintMaterial.joins( :eve_item ).where( 'eve_items.market_group_id' => market_groups_to_destroy_ids ).pluck( :blueprint_id )
      # Blueprint.where( id: blueprints_linked_to_items_ids ).destroy_all
      #
      # MarketGroup.where( cpp_market_group_id: market_groups_to_destroy_ids ).destroy_all

    end
  end

end

