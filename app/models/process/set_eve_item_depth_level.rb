# The depth level is used to to compute the cost in the right order.
# The highest level is 0, and it can go as deep as it can.
# You will have to compute the cost of the lowest level first and then go up to 0

module Process

  class SetEveItemDepthLevel

    def set

      Banner.p 'About to set eve item depth level'

      blueprints = YAML::load_file('data/parsed_blueprints.yaml')
      materials_use = {}

      blueprints.values.each do |bp|
        bp[:materials].each do |m|
          materials_use[ m[:type_id] ] = bp[:produced_cpp_type_id]

          if m[:type_id] == bp[:produced_cpp_type_id]
            puts "Material loop detcted in blueprint id #{bp[:cpp_blueprint_id]}."
            pp bp
            exit
          end
        end
      end

      types = YAML::load_file('data/types.yaml')
      types.each do |type_id, type|
        type[:production_level] = 0

        loop do
          materials_use_id = materials_use[ type[:cpp_eve_item_id] ]
          p materials_use_id
          if materials_use_id
            type[:production_level] += 1
            materials_use_id = materials_use[ materials_use_id ]
          else
            break
          end
        end
      end

      File.open('data/types.yaml', 'w') {|f| f.write types.to_yaml }

      p :finished

    end
  end
end
