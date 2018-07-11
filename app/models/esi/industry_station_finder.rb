module Esi
  class IndustryStationFinder < Download

    REQUIRED_SERVICES = %w( cloning factory labratory office-rental )
    def initialize( debug_request: false )
      super( 'universe/systems/', {}, debug_request: debug_request )
    end

    def fill_station_table
      ActiveRecord::Base.transaction do
        sub_fill_station_table
      end
    end

    private

    def sub_fill_station_table
      systems = get_page_retry_on_error

      stations_office_prices = []

      systems.each do |system_id|
        puts "Checking system : #{system_id}"

        @rest_url = "universe/systems/#{system_id}/"
        system_data = get_page_retry_on_error

        stations = system_data['stations']
        if stations
          stations.each do |station_id|
            puts "\tChecking station : #{station_id}"

            @rest_url = "universe/stations/#{station_id}/"
            station_data = get_page_retry_on_error

            trade_hub_station = Station.find_by_cpp_station_id( station_id )

            station = StationDetail.where( cpp_station_id: station_id ).first_or_initialize
            station.name = station_data['name']
            station.office_rental_cost = station_data['office_rental_cost']
            station.services = station_data['services']
            station.cpp_system_id = system_id
            station.station_id = trade_hub_station&.id

            station.save!
          end
        end
      end
    end
  end
end
