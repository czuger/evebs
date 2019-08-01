require 'set'

module Esi
  class DownloadUniverseSystems < Download

    def initialize( debug_request: false )
      super( 'universe/systems', {}, debug_request: debug_request )
    end

    def update
      puts 'Updating Systems Data'

      gomex = User.find_by_name( 'Gomex' )

      set_auth_token( gomex )

      systems_ids = get_all_pages

      puts "About to check #{systems_ids.count} systems"
      count = 0

        systems_ids.each do |system_id|

          count += 1

          if count % 100 == 0
            puts "#{count} systems checked."
          end

          @rest_url = "universe/systems/#{system_id}/"
          system_data = get_page_retry_on_error

          next unless system_data['star_id']

        ActiveRecord::Base.transaction do
          s = UniverseSystem.where( cpp_system_id: system_data['system_id'] ).first_or_initialize

          # pp system_data

          s.name = system_data['name']
          s.cpp_constellation_id = system_data['constellation_id']
          s.cpp_star_id = system_data['star_id']
          s.security_class = system_data['security_class']
          s.security_status = system_data['security_status']
          s.stations_ids = system_data['stations'] || []
          s.save!

          update_universe_station_table s, system_data['stations']
        end
      end
    end

    private

    def update_universe_station_table( system, stations_data )

      if stations_data
        stations_data.each do |station_id|
          # puts "\tChecking station : #{station_id}"

          @rest_url = "universe/stations/#{station_id}/"
          station_data = get_page_retry_on_error

          trade_hub_station = Station.find_by_cpp_station_id( station_id )

          station = UniverseStation.where(cpp_station_id: station_id ).first_or_initialize
          station.name = station_data['name']
          station.office_rental_cost = station_data['office_rental_cost']
          station.services = station_data['services']
          station.cpp_system_id = system.cpp_system_id
          station.station_id = trade_hub_station&.id
          station.security_status = system.security_status
          station.universe_system = system

          station.save!
        end
      end
    end

  end
end
