require 'set'

module Process
  class UpdateUniverseRegions

    def update
      Misc::Banner.p 'About to update regions and all sub data'

      regions = YAML.load_file('data/regions.yaml')

      Region.transaction do
        regions.each do |regions|
          create_region regions
        end
      end

      Misc::Banner.p 'Regions and sub data update finished'
    end

    private

    def create_region( region )
      db_region = UniverseRegion.find_or_create_by!( cpp_region_id: region[:id] ) do |r|
        r.name = region[:name]
      end

      region[:constellations].each do |constellation|
        create_constellation( constellation, db_region.id )
      end
    end

    def create_constellation( constellation, region_id )
      db_constellation = UniverseConstellation.find_or_create_by!( cpp_constellation_id: constellation[:id] ) do |c|
        c.name = constellation[:name]
        c.universe_region_id = region_id
      end

      constellation[:systems].each do |system|
        update_system( system, db_constellation.id )
      end
    end

    def update_system( system, constellation_id )
      s = UniverseSystem.where( cpp_system_id: system[:id] ).first_or_initialize

      s.name = system[:name]
      s.universe_constellation_id = constellation_id
      s.cpp_star_id = system[:star_id]
      s.security_class = system[:security_class]
      s.security_status = system[:security_status]

      s.save!

      system[:stations].each do |station|
        update_station( station, s.id, s.security_status )
      end
    end

    def update_station( station, system_id, security_status )
      trade_hub_station = Station.find_by_cpp_station_id( station[:id] )

      station = UniverseStation.where(cpp_station_id: station[:id] ).first_or_initialize
      station.name = station[:name]
      station.office_rental_cost = station[:office_rental_cost]
      station.services = station[:services]
      station.station_id = trade_hub_station&.id
      station.security_status = security_status
      station.universe_system_id = system_id

      station.save!
    end

  end
end
