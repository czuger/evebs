module Esi

  class ParseBlueprintsFile < Download

    def process
      parse
      check
    end

    private

    def parse

      Banner.p 'About to parse cpp blueprint file'

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
            puts 'Blueprint produce more than one item'
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

    def check
      Banner.p 'About to check blueprints and get names'

      blueprints = YAML::load_file('data/parsed_blueprints.yaml')
      new_blueprints_list = []
      eve_items_to_check_cpp_ids = Set.new

      puts "#{blueprints.count} blueprints to check."
      check_count = 0

      blueprints.each do |bp|

        check_count += 1
        puts "#{check_count} blueprints checked" if check_count % 100 == 0

        # pp bp

        @rest_url = "universe/types/#{bp[:cpp_blueprint_id]}/"

        begin
          bp_remote_data = get_page

        rescue Esi::Errors::NotFound
          puts "Data not found for blueprint id : #{bp[:cpp_blueprint_id]}"
          next
        end

        next unless bp_remote_data['published']

        bp['name'] = bp_remote_data['name']
        new_blueprints_list << bp

        eve_items_to_check_cpp_ids = add_items_to_check( eve_items_to_check_cpp_ids, bp )
      end

      File.open('data/parsed_blueprints.yaml', 'w') {|f| f.write new_blueprints_list.to_yaml }
      File.open('data/type_ids_to_download.yaml', 'w') {|f| f.write eve_items_to_check_cpp_ids.to_a.to_yaml }
    end

    def add_items_to_check( eve_items_to_check_cpp_ids, bp )
      eve_items_to_check_cpp_ids << bp[:produced_cpp_type_id]
      eve_items_to_check_cpp_ids += bp[:materials].map{ |m| m[:type_id] }
      eve_items_to_check_cpp_ids
    end

  end
end
