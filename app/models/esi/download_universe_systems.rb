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

      ActiveRecord::Base.transaction do
        systems_ids.each do |system_id|

          count += 1

          if count % 100 == 0
            puts "#{count} systems checked."
          end

          @rest_url = "universe/systems/#{system_id}/"
          system_data = get_page_retry_on_error

          next unless system_data['star_id']

          s = UniverseSystem.where( cpp_system_id: system_data['system_id'] ).first_or_initialize

          # pp system_data

          s.name = system_data['name']
          s.cpp_constellation_id = system_data['constellation_id']
          s.cpp_star_id = system_data['star_id']
          s.security_class = system_data['security_class']
          s.security_status = system_data['security_status']
          s.stations_ids = system_data['stations'] || []
          s.save!

        end
      end
    end
  end
end
