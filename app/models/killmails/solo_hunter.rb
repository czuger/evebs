module Killmails
  class SoloHunter

    def show

      gci = Esi::GetCharacterInfo.new
      get_corp_i = Esi::GetCorporationInfo.new
      kills_list = []

      Esi::GetFactions.new.get_ids.each do |faction_id|
        @request = open( "https://zkillboard.com/api/factionID/#{faction_id}/solo/kills/pastSeconds/14400/" )
        json_result = @request.read
        faction_result = JSON.parse( json_result )

        faction_result.each do |result|
          kill = Esi::GetKillmail.new( result['killmail_id'], result['zkb']['hash'] ).get

          p kill

          solar_system_name = UniverseSystem.where( cpp_system_id: kill['solar_system_id'] ).first.name
          kill_time = kill['killmail_time']

          kill['attackers'].each do |attacker|
            attacker_id = attacker['character_id']
            corporation_id = attacker['corporation_id']

            next unless attacker_id
            attacker_data = gci.get( attacker_id )
            corporation_data = get_corp_i.get( corporation_id )

            kills_list << "#{corporation_data['name']}-#{attacker_data['name']} at #{kill_time} killed somebody in #{solar_system_name} "
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