module Killmails
  class SoloHunter

    def show

      gci = Esi::GetCharacterInfo.new
      get_corp_i = Esi::GetCorporationInfo.new
      kills_list = []

      Esi::GetFactions.new.get_ids.each do |faction_id|
        @request = open( "https://zkillboard.com/api/factionID/#{faction_id}/solo/kills/pastSeconds/3600/" )
        json_result = @request.read
        faction_result = JSON.parse( json_result )

        faction_result.each do |result|
          kill = Esi::GetKillmail.new( result['killmail_id'], result['zkb']['hash'] ).get

          # p kill

          solar_system = UniverseSystem.where( cpp_system_id: kill['solar_system_id'] ).first

          next if solar_system.security_status*10 <= 0

          solar_system_name = "#{solar_system.name}(#{(solar_system.security_status*10).round})"

          kill_time = Time.parse(kill['killmail_time']).strftime('%R')

          victim_data = EveItem.where( cpp_eve_item_id: kill['victim']['ship_type_id'] ).first
          victim_name = victim_data ? victim_data.name : kill['victim']['ship_type_id']

          kill['attackers'].each do |attacker|
            attacker_id = attacker['character_id']
            next unless attacker_id

            corporation_id = attacker['corporation_id']

            ship_data = EveItem.where( cpp_eve_item_id: attacker['ship_type_id'] ).first
            ship_name = ship_data ? ship_data.name : attacker['ship_type_id'].to_s
            # p ship_name

            attacker_data = gci.get( attacker_id )
            corporation_data = get_corp_i.get( corporation_id )

            out_string = sprintf( '%-20s%-50s%-30s%-6s%-40s%-40s', solar_system_name,
                                  corporation_data['name'], attacker_data['name'], kill_time, ship_name, victim_name )

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