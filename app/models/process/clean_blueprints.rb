module Process

  # After market and items check, some items required by blueprints could disappear.
  # So we need to check them again and clean impacted blueprints
  class CleanBlueprints

    def clean

      Banner.p 'About to clean blueprint impacted by items deletion'

      blueprints = YAML::load_file('data/parsed_blueprints.yaml')
      items_ids = YAML::load_file('data/types.yaml').keys.to_set

      to_remove_blueprints = Set.new

      blueprints.each do |blueprint_id, blueprint|

        # We remove the blueprint if the produced item is not in the list of the final items
        to_remove_blueprints << blueprint_id unless items_ids.include?( blueprint[:produced_cpp_type_id] )

        # We remove the blueprint if any of the materials required is not in the list of final items
        blueprint[:materials].each do |material|
          to_remove_blueprints << blueprint_id unless items_ids.include?( material[:type_id] )
        end

      end

      to_remove_blueprints.each do |bp_id|
        blueprints.delete( bp_id )
      end

      File.open('data/parsed_blueprints.yaml', 'w') {|f| f.write blueprints.to_yaml }
    end

  end
end
