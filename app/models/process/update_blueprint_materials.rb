module Process

  class UpdateBlueprintMaterials

    def update
      Misc::Banner.p 'About to update blueprint_materials'

      blueprints = YAML::load_file('data/parsed_blueprints.yaml')

      eve_items_cpp_to_syntetic_key_conversion_hash = Hash[ EveItem.pluck( :cpp_eve_item_id, :id ) ]
      blueprint_cpp_to_syntetic_key_conversion_hash = Hash[ Blueprint.pluck( :cpp_blueprint_id, :id ) ]

      blueprints.each do |blueprint_id, blueprint|
        blueprint_id = blueprint_cpp_to_syntetic_key_conversion_hash[blueprint_id]

        blueprint[:materials].each do |material|
          eve_item_id = eve_items_cpp_to_syntetic_key_conversion_hash[material[:type_id]]

          on_db_material = BlueprintMaterial.where( eve_item_id: eve_item_id, blueprint_id: blueprint_id ).first_or_initialize
          on_db_material.required_qtt = material[:quantity]

          on_db_material.save!
        end
      end
    end
  end

end

