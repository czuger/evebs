module Esi
  class IndustryStationFinder < Download

    REQUIRED_SERVICES = %w( cloning factory labratory office-rental )
    JITA_CPP_SYSTEM_ID = 30000142

    def initialize( debug_request: false )
      super( 'universe/systems/', {}, debug_request: debug_request )
    end

    def find_stations
      StationDetail.where( 'services @> ARRAY[?]::varchar[]', [ :factory, :labratory, 'office-rental', :cloning ] )
        .where( 'security_status >= 0.5 AND jita_distance < 10 AND office_rental_cost < 1000000' )
        .order( 'jita_distance, office_rental_cost' ).each do |station|

        puts '%-90s %11.0f % 4.2f %3d %s' %
                 [ station.name, station.office_rental_cost, station.security_status, station.jita_distance, station.industry_costs_indices ]
      end
    end

    def find_reaction_stations
      StationDetail.where( 'services @> ARRAY[?]::varchar[]', [ :reactions ] )
          .where( 'jita_distance < 13' )
          .order( 'jita_distance' ).each do |station|

        puts '%-90s %11.0f % 4.2f %3d %s' %
                 [ station.name, station.office_rental_cost, station.security_status, station.jita_distance, station.industry_costs_indices ]
      end
    end

    def fill_station_table
      ActiveRecord::Base.transaction do
        sub_fill_station_table
      end
    end

    def update_security_status
      StationDetail.distinct.pluck( :cpp_system_id ).each do |cpp_system_id|
        puts "Retrieving status for #{cpp_system_id}"

        @rest_url = "universe/systems/#{cpp_system_id}/"
        @params['flag'] = :secure
        system_data = get_page_retry_on_error

        StationDetail.where( cpp_system_id: cpp_system_id ).update_all( security_status: system_data['security_status'] )
      end
    end

    def update_industry_systems
      @rest_url = 'industry/systems/'
      systems_datas = get_all_pages

      systems_datas.each do |sd|
        cost_indices = Hash[ sd['cost_indices'].map{ |e| [ e['activity'], (e['cost_index']*100).round(1) ] } ]
        StationDetail.where( cpp_system_id: sd['solar_system_id'] ).update_all( industry_costs_indices: cost_indices )
      end
    end

    def update_jita_distance
      StationDetail.distinct.pluck( :cpp_system_id ).each do |cpp_system_id|
        # puts "Retrieving status for #{cpp_system_id}"

        @rest_url = "route/#{cpp_system_id}/#{JITA_CPP_SYSTEM_ID}/"

        begin
          path = get_page_retry_on_error
        rescue Esi::Errors::NotFound
        end

        StationDetail.where( cpp_system_id: cpp_system_id ).update_all( jita_distance: path.count ) if path
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
