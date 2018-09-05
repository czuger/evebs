# The depth level is used to to compute the cost in the right order.
# The highest level is 0, and it can go as deep as it can.
# You will have to compute the cost of the lowest level first and then go up to 0

module Process

  class SetEveItemDepthLevel

    def set

      Banner.p 'About to set eve item depth level'

      blueprints = YAML::load_file('data/blueprints.yaml')
      final_blueprints_list = []

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

          final_blueprints_list << {
              cpp_blueprint_id: blueprint_id,  produced_cpp_type_id: products.first['typeID'], nb_runs: blueprint_data['maxProductionLimit'],
              prod_qtt: products.first['quantity'], materials: materials }
        end
      end

      File.open('data/parsed_blueprints.yaml', 'w') {|f| f.write final_blueprints_list.to_yaml }
    end

  end
end
