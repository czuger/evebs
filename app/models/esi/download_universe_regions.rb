require 'set'

module Esi
  class DownloadUniverseRegions < Download

    def initialize( debug_request: false )
      super( 'universe/regions', {}, debug_request: debug_request )
      @regions = []
    end

    def download
      Misc::Banner.p 'Downloading regions and all sub data'

      download_regions
    end

    private

    def download_regions
      regions_ids = get_all_pages

      regions_ids.each do |region_id|
        @rest_url = "universe/regions/#{region_id}/"
        region_data = get_page_retry_on_error

        region = { id: region_id, name: region_data['name'], constellations: [] }

        region_data['constellations'].each do |constellation_id|
          region[:constellations] << download_constellation( constellation_id )
        end
        @regions << region

        write_data
      end

    end

    def download_constellation( constellation_id )
      @rest_url = "universe/constellations/#{constellation_id}/"
      constellation_data = get_page_retry_on_error

      constellation = { id: constellation_id, name: constellation_data['name'], systems: [] }

      constellation_data['systems'].each do |system_id|
        constellation[:systems] << download_system( system_id )
      end

      constellation
    end

    def download_system( system_id )
      @rest_url = "universe/systems/#{system_id}/"
      system_data = get_page_retry_on_error

      system = { id: system_id, name: system_data['name'] }

      system[:constellation_id] = system_data['constellation_id']
      system[:star_id] = system_data['star_id']
      system[:security_class] = system_data['security_class']
      system[:security_status] = system_data['security_status']
      system[:stations] = []

      # region_data['systems'].each do |system_id|
      #   data = download_system( data, system_id )
      # end

      stations = system_data['stations'] || []

      stations.each do |station_id|
        system[:stations] << update_station( station_id )
      end

      system
    end

    def update_station( station_id )
      @rest_url = "universe/stations/#{station_id}/"
      station_data = get_page_retry_on_error

      station = { id: station_id, name: station_data['name'] }

      station[:office_rental_cost] = station_data['office_rental_cost']
      station[:services] = station_data['services']

      station
    end

    def write_data
      File.open( 'data/regions.yaml', 'w' ) do |f|
        f.write( @regions.to_yaml )
      end
    end

  end
end
