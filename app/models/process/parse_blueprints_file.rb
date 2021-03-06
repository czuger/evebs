module Process

  class ParseBlueprintsFile

    def parse

      Misc::Banner.p 'About to parse cpp blueprint file'

      blueprints = YAML::load_file('data/blueprints.yaml')
      final_blueprints_hash = {}

      blueprints.each do |bp|

        blueprint_id, blueprint_data = bp
        if blueprint_data['activities']['manufacturing']
          materials = blueprint_data['activities']['manufacturing']['materials']
          products = blueprint_data['activities']['manufacturing']['products']

          # pp bp unless materials
          next unless materials

          # pp bp unless products
          next unless products

          if products.count > 1
            puts 'Blueprint produce more than one item.'
            pp bp
            next
          end

          materials.map!{ |m| { quantity: m[ 'quantity' ], type_id: m[ 'typeID' ] } }

          material_loop = false
          materials.each do |m|
            if m[:type_id] == products.first['typeID']
              puts "Blueprint #{blueprint_id} produce a required material. Production loop. Blueprint skipped."
              material_loop = true
              break
            end
          end
          next if material_loop

          final_blueprints_hash[blueprint_id] = {
              cpp_blueprint_id: blueprint_id,  produced_cpp_type_id: products.first['typeID'], nb_runs: blueprint_data['maxProductionLimit'],
              prod_qtt: products.first['quantity'], materials: materials }
        end
      end

      File.open('data/parsed_blueprints.yaml', 'w') {|f| f.write final_blueprints_hash.to_yaml }
    end

  end
end
