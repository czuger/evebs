module Esi

  class DownloadBlueprints < Download

    def download
      Banner.p 'About to download blueprints extra data'

      blueprints = YAML::load_file('data/parsed_blueprints.yaml')
      @eve_items_to_check_cpp_ids = Set.new

      if @verbose_output
        puts "#{blueprints.count} blueprints to check."
        check_count = 0
      end

      blueprints.each do |bp_id, bp|

        if @verbose_output
          check_count += 1
          puts "#{check_count} blueprints checked" if check_count % 100 == 0
        end

        # pp bp

        @rest_url = "universe/types/#{bp[:cpp_blueprint_id]}/"

        begin
          bp_remote_data = get_page

        rescue Esi::Errors::NotFound
          puts "Data not found for blueprint id : #{bp[:cpp_blueprint_id]}"
          blueprints.delete(bp_id)
          next
        end

        unless bp_remote_data['published']
          blueprints.delete(bp_id)
          next
        end

        bp['name'] = bp_remote_data['name']

        add_items_to_check( bp )
      end

      File.open('data/parsed_blueprints.yaml', 'w') {|f| f.write blueprints.to_yaml }
      File.open('data/type_ids_to_download.yaml', 'w') {|f| f.write @eve_items_to_check_cpp_ids.to_a.to_yaml }
    end

    def add_items_to_check( bp )
      @eve_items_to_check_cpp_ids << bp[:produced_cpp_type_id]
      @eve_items_to_check_cpp_ids += bp[:materials].map{ |m| m[:type_id] }
    end

  end
end
