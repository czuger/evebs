module Process

  # This have to be run after the update of the items. Computing the costs is a recursive process.
  class UpdateEveItemsCosts

    # Recompute the cost for all items
    def update
      lowest_production_level = File.open( 'data/lowest_production_level' ).read.to_i

      Sql::UpdateCostsBaseItems.update

      lowest_production_level.upto( 0 ).each do |level|
        Sql::UpdateCostsCraftedItems.update( level )
      end
    end
  end
end

