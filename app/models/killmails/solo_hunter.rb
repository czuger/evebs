module Killmails
  class SoloHunter

    def show

      gci = Esi::GetCharacterInfo.new
      get_corp_i = Esi::GetCorporationInfo.new
      gsi = Esi::GetSystemInfo.new
      kills_list = []

      Esi::GetFactions.new.get_ids.each do |faction_id|
        puts "Fetching #{faction_id}"

        @request = open( "https://zkillboard.com/api/factionID/#{faction_id}/kills/pastSeconds/3600/" )
        sleep 1
        json_result = @request.read
        faction_result = JSON.parse( json_result )

        faction_result.each do |result|
          kill = Esi::GetKillmail.new( result['killmail_id'], result['zkb']['hash'] ).get

          # p kill

          solar_system = gsi.get( kill['solar_system_id'] )

          # p solar_system

          next if solar_system.security_status*10 <= 0

          solar_system_name = "#{solar_system.name}(#{(solar_system.security_status*10).round})"

          kill_time = DateTime.parse(kill['killmail_time']).localtime.strftime('%R')

          kill['attackers'].each do |attacker|
            attacker_id = attacker['character_id']
            next unless attacker_id

            corporation_id = attacker['corporation_id']

            # p ship_name

            attacker_data = gci.get( attacker_id )
            corporation_data = get_corp_i.get( corporation_id )

            out_string = sprintf( '%-20s%-50s%-30s%-6s', solar_system_name,
                                  corporation_data['name'], attacker_data['name'], kill_time )

            # p out_string

            kills_list << out_string
          end
        end
      end

      kills_list.sort!

      kills_list.each do |k|
        puts k
      end
    end

  end
end