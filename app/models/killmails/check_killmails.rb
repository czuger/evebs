require 'open-uri'
require 'json'

module Misc
  class CheckKillmails

    def update
      count = 0

      UniverseSystem.transaction do
        UniverseSystem.all.each do |system|
          @request = open( "https://zkillboard.com/api/stats/solarSystemID/#{system.cpp_system_id}/" )
          json_result = @request.read
          parsed_result = JSON.parse( json_result )

          count += 1

          if count % 100 == 0
            puts "#{count} killmails checked."
          end

          months_data = parsed_result['months']

          next unless months_data

          # pp months_data

          current_month_data = months_data[ ( Time.now.to_date - 1.month ).strftime( '%Y%m' ) ]
          previous_month_data = months_data[ ( Time.now.to_date - 2.month ).strftime( '%Y%m' ) ]

          system.kill_stats_current_month = current_month_data['shipsDestroyed'] if current_month_data
          system.kill_stats_last_month = previous_month_data['shipsDestroyed'] if previous_month_data

          system.save!
        end
      end
    end

  end
end