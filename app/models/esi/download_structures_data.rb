require 'set'

module Esi
  class DownloadStructuresData < Download

    def initialize( debug_request: false )
      super( 'universe/structures/', {}, debug_request: debug_request )
    end

    def update
      puts 'Updating Structures Data'

      gomex = User.find_by_name( 'Gomex' )
      structures_types = {}

      solars_systems = TradeHub.pluck( :eve_system_id )

      # pp gomex

      set_auth_token( gomex )

      structures_ids = get_all_pages

      puts "About to check #{structures_ids.count} structures"
      count = 0

      ActiveRecord::Base.transaction do
        structures_ids.each do |structure_id|

          count += 1

          if count % 100 == 0
            puts "#{count} structures checked."
          end

          @rest_url = "universe/structures/#{structure_id}/"
          structure_data = get_page_retry_on_error

          structures_types[ structure_data[ 'type_id' ] ] ||= 0
          structures_types[ structure_data[ 'type_id' ] ] += 1

          if structure_data[ 'type_id' ] == 35834
            puts "Found a Keepstar named #{structure_data[ 'name' ]}"

            @rest_url = "universe/systems/#{structure_data[ 'solar_system_id' ]}/"
            systeme_data = get_page
            puts "In #{systeme_data['name']}"

            @rest_url = "universe/systems/#{structure_data[ 'owner_id' ]}/"
            corpo_data = get_page
            puts "Owned by #{corpo_data['name']}"
          end

          next unless solars_systems.include?( structure_data[ 'solar_system_id' ] )

          th = TradeHub.find_by_eve_system_id( structure_data[ 'solar_system_id' ] )

          s = Structure.where( trade_hub_id: th.id, cpp_structure_id: structure_data[ 'solar_system_id' ] ).first_or_initialize
          s.save!

        end
      end

      structures_types.each do |type_id, amount|
        @rest_url = "universe/types/#{type_id}/"
        type_info = get_page

        puts "#{type_info['name']} (#{type_id}) : #{amount}"
      end

    end

  end
end

