require 'set'

module Esi
  class DownloadStructuresData < Download

    def initialize( debug_request: false )
      super( 'universe/structures/', {}, debug_request: debug_request )
    end

    def update
      puts 'Updating Structures Data'

      gomex = User.find_by_name( 'Gomex' )
      set_auth_token( gomex )

      structures_ids = get_all_pages

      puts "About to check #{structures_ids.count} structures"
      count = 0

      # ActiveRecord::Base.transaction do
        structures_ids.each do |structure_id|

          next if Structure.where( cpp_structure_id: structure_id, forbidden: true ).exists?

          count += 1

          if count % 100 == 0
            puts "#{count} structures checked."
          end

          structure = nil

          begin
            @rest_url = "universe/structures/#{structure_id}/"
            structure_data = get_page

            solar_system = UniverseSystem.find_by_cpp_system_id( structure_data[ 'solar_system_id' ] )
            structure = Structure.where( universe_system_id: solar_system.id, cpp_structure_id: structure_id ).first_or_initialize

            @rest_url = "markets/structures/#{structure_id}/"
            structure_data = get_page

            p structure_data

            structure.forbidden = false
            structure.orders_count_pages = @pages_count
            structure.save!

          rescue Esi::Errors::Forbidden
            puts 'Structure access was denied'

            sleep 1

            if structure
              structure.forbidden = true
              structure.save!

              if @errors_limit_remain.to_i <= 25
                sleep( 10 )
              end
            end
          end
        end
      # end
    end
  end
end