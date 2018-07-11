module Esi
  class IndustryStationFinder < Download

    REQUIRED_SERVICES = %w( cloning factory labratory office-rental )
    def initialize( debug_request: false )
      super( 'universe/systems/', {}, debug_request: debug_request )
    end

    def get
      systems = get_page_retry_on_error

      stations_office_prices = []

      systems.each do |system_id|
        puts "Checking system : #{system_id}"

        @rest_url = "universe/systems/#{system_id}/"
        system_data = get_page_retry_on_error

        stations = system_data['sta tions']
        if stations
          stations.each do |station_id|
            puts "\tChecking station : #{station_id}"

            @rest_url = "universe/stations/#{station_id}/"
            station_data = get_page_retry_on_error

            if ( REQUIRED_SERVICES - station_data['services'] ).empty?
              stations_office_prices << [ station_data['office_rental_cost'], station_data['name'] ]
            end

          end
        end
      end

      stations_office_prices = stations_office_prices.sort.reverse

      pp stations_office_prices
    end
  end
end
