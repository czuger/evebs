module Setup::UpdateBlueprints

  def get_blueprints_array_from_cpp_sources

    blueprints_array = []

    Setup::CppSourcesIndustryBlueprint.all.each do |blueprint|

      if blueprint.products.count >= 1

        blueprint_id = blueprint.typeID

        raise "Blueprint produce more than one item : #{bp.inspect}" if blueprint.products.count > 1

        produced_item = blueprint.products.first

        produced_item_id = produced_item.productTypeID
        produced_item_qtt = produced_item.quantity
        max_production_limit = blueprint.maxProductionLimit

        blueprint_hash = {
          blueprint_id: blueprint_id, cpp_produced_type_id: produced_item_id,
          produced_item_qtt: produced_item_qtt, max_production_limit: max_production_limit,
          materials: blueprint.materials.map{ |m| { cpp_material_type_id: m.materialTypeID, quantity: m.quantity } }
        }
        blueprint_hash[ :cpp_consumed_material_type_ids ] = blueprint_hash[ :materials ].map{ |m| m[ :cpp_material_type_id ] }

        blueprints_array << blueprint_hash
      end
    end
    blueprints_array
  end

end